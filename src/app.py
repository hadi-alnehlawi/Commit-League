import os, json
from requests import request as req
from flask import Flask, redirect, url_for, jsonify, abort, request, render_template, session
from flask_dance.contrib.github import make_github_blueprint, github
# from mapping import Repo, Contributor, Repository
from mapping.Repository import Repository
from mapping.Contributor import Contributor
from mapping.Repo import Repo
from functools import wraps
from model import setup_db
import datetime
from flask_login import logout_user, LoginManager

github_bp = make_github_blueprint()


def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")
    app.config["GITHUB_OAUTH_CLIENT_ID"] = os.environ.get(
        "GITHUB_OAUTH_CLIENT_ID")
    app.config["GITHUB_OAUTH_CLIENT_SECRET"] = os.environ.get(
        "GITHUB_OAUTH_CLIENT_SECRET")
    app.register_blueprint(github_bp, url_prefix="/login")
    # setup db to store OAuth tokens
    setup_db(app, github_bp)
    # environment varaibales
    REPOSITORY = os.environ.get("REPOSITORY")
    OWNER = os.environ.get("OWNER")
    url = f"repos/{OWNER}/{REPOSITORY}"

    def authorizing(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not github.authorized:
                return redirect(url_for("github.login"))
            else:
                ACCESS_TOKEN = app.blueprints['github'].token['access_token']
                print("ACCESS_TOKEN=", ACCESS_TOKEN)
                return f()

        return wrapper

    def get_all_contributors(repo):
        body = repo.to_dict()
        return jsonify({"success": True, "body": body})

    def get_one_contributor(login):
        contributor = Contributor(login=login, load_stats=True)
        return jsonify({"success": True, "body": contributor.to_dict()})

    @app.route("/")
    @authorizing
    def index():
        contribtuor_res = Repository.get_contribtuor_res()
        if contribtuor_res.status_code == 404:
            abort(404)
        elif contribtuor_res.status_code == 403:
            abort(403)
        else:
            return render_template('index.html')

    @app.route("/contributors")
    @authorizing
    def contributors_endpoint():
        query_string = request.query_string
        if not query_string:
            # no query string
            repo = Repo()
            return get_all_contributors(repo)
        else:
            # get login of query string
            login = request.args.get('login')
            return get_one_contributor(login=login)

    @app.route("/logout")
    def logout():
        ACCESS_TOKEN = app.blueprints['github'].token['access_token']
        CLIENT_ID = os.environ.get("GITHUB_OAUTH_CLIENT_ID")
        payload = "{\"access_token\": \"%s\"}" % (ACCESS_TOKEN)
        logout_url = f"https://api.github.com/applications/{CLIENT_ID}/grant"
        headers = {
            'Authorization':
            'Basic NjliYTRiMTBhNGE0Y2RhM2IxNzQ6MDJlN2FmYTQ1NTIxYmYyMzBhYzNkNTg4MGQ0MWIwNGRlMWUzYWY1OQ==',
            'Content-Type': 'application/json',
            'Cookie': '_octo=GH1.1.2130686163.1612643408; logged_in=no'
        }
        resp = req("DELETE", logout_url, headers=headers, data=payload)
        if resp.ok:
            del app.blueprints['github'].token
            session.clear()
            return "Ok"
        else:
            abort(401)

    @app.errorhandler(404)
    def error_404(error):
        return jsonify({"success": False, "message": "page not found"}), 404

    @app.errorhandler(403)
    def error_403(error):
        return jsonify({"success": False, "message": "forbidded call"}), 403

    return app


app = create_app()

if __name__ == '__main__':
    app.debug = True
    # app.env = "development"
    app.run(host='0.0.0.0', port=5000)