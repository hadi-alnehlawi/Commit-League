--
-- PostgreSQL database dump
--

-- Dumped from database version 13.1 (Debian 13.1-1.pgdg100+1)
-- Dumped by pg_dump version 13.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: flask_dance_oauth; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.flask_dance_oauth (
    id integer NOT NULL,
    provider character varying(50) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    token json NOT NULL
);


ALTER TABLE public.flask_dance_oauth OWNER TO postgres;

--
-- Name: flask_dance_oauth_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.flask_dance_oauth_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.flask_dance_oauth_id_seq OWNER TO postgres;

--
-- Name: flask_dance_oauth_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.flask_dance_oauth_id_seq OWNED BY public.flask_dance_oauth.id;


--
-- Name: flask_dance_oauth id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flask_dance_oauth ALTER COLUMN id SET DEFAULT nextval('public.flask_dance_oauth_id_seq'::regclass);


--
-- Data for Name: flask_dance_oauth; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.flask_dance_oauth (id, provider, created_at, token) FROM stdin;
\.


--
-- Name: flask_dance_oauth_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.flask_dance_oauth_id_seq', 4, true);


--
-- Name: flask_dance_oauth flask_dance_oauth_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flask_dance_oauth
    ADD CONSTRAINT flask_dance_oauth_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

