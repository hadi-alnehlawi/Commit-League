# Commit-League

The challenge is to generate an HTML page that lists the top contributors of a Github repository, along with some additional information.
Using the [Github API](https://developer.github.com/v3/), to collect data from the public repository,[Flask](https://github.com/pallets/flask) and generate an HTML page with the following information:

Repository's full name ({owner}/{repo} e.g. avidity/some-repo) and description
List of contributors, listed by number of contribution in descending order
For each contributor:
Number of contributions
Date of first contribution
Date of last contribution
Average commits, additions and deletions per week over the whole period
Most active period

Requests to the Github API made by your application must be authenticated using OAuth2 token (check the API documentation for more information).

# Desing

The solution based on the idea of requesting data from Githib API and deserializing the josn responses into OOP object and doing the processing on run-time.

## Backend

`Python` programming language with `Flask` framework is used as a a tech stack. OAuth2 tokens are stored in centrazlied database `PostgresSQL`.

This approach knows how to store and retrieve OAuth tokens from some kind of persistent storage.

## Frontend

`HTML` template file which fetchs data from backend API endpoints. The technology used: `javascrip` along with `jQuery` to handle the fetch processing.
