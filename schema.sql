--
-- PostgreSQL database dump
--

-- Dumped from database version 15.3
-- Dumped by pg_dump version 15.4

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

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: clearskyprod_user
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO clearskyprod_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: api; Type: TABLE; Schema: public; Owner: clearskyprod_user
--

CREATE TABLE public.api (
    key character(32) NOT NULL,
    date_added timestamp without time zone,
    valid boolean,
    owner text,
    owner_id text,
    environment text
);


ALTER TABLE public.api OWNER TO clearskyprod_user;

--
-- Name: block_temporary_table; Type: TABLE; Schema: public; Owner: clearskyprod_user
--

CREATE TABLE public.block_temporary_table (
    last_processed_did text NOT NULL
);


ALTER TABLE public.block_temporary_table OWNER TO clearskyprod_user;

--
-- Name: blocklists; Type: TABLE; Schema: public; Owner: clearskyprod_user
--

CREATE TABLE public.blocklists (
    user_did text,
    blocked_did text,
    block_date timestamp with time zone,
    cid text,
    uri text
);


ALTER TABLE public.blocklists OWNER TO clearskyprod_user;

--
-- Name: last_did_created_date; Type: TABLE; Schema: public; Owner: clearskyprod_user
--

CREATE TABLE public.last_did_created_date (
    last_created timestamp with time zone NOT NULL
);


ALTER TABLE public.last_did_created_date OWNER TO clearskyprod_user;

--
-- Name: mutelists; Type: TABLE; Schema: public; Owner: clearskyprod_user
--

CREATE TABLE public.mutelists (
    url text,
    uri text NOT NULL,
    did text,
    cid text NOT NULL,
    name text,
    created_date text,
    description text
);


ALTER TABLE public.mutelists OWNER TO clearskyprod_user;

--
-- Name: mutelists_users; Type: TABLE; Schema: public; Owner: clearskyprod_user
--

CREATE TABLE public.mutelists_users (
    list text,
    cid text NOT NULL,
    did text,
    date_added text,
    uri text
);


ALTER TABLE public.mutelists_users OWNER TO clearskyprod_user;

--
-- Name: top_block; Type: TABLE; Schema: public; Owner: clearskyprod_user
--

CREATE TABLE public.top_block (
    did text,
    count integer,
    list_type text
);


ALTER TABLE public.top_block OWNER TO clearskyprod_user;

--
-- Name: top_twentyfour_hour_block; Type: TABLE; Schema: public; Owner: clearskyprod_user
--

CREATE TABLE public.top_twentyfour_hour_block (
    did text,
    count integer,
    list_type text
);


ALTER TABLE public.top_twentyfour_hour_block OWNER TO clearskyprod_user;

--
-- Name: user_prefixes; Type: TABLE; Schema: public; Owner: clearskyprod_user
--

CREATE TABLE public.user_prefixes (
    handle text NOT NULL,
    prefix1 text NOT NULL,
    prefix2 text NOT NULL,
    prefix3 text NOT NULL
);


ALTER TABLE public.user_prefixes OWNER TO clearskyprod_user;

--
-- Name: users; Type: TABLE; Schema: public; Owner: clearskyprod_user
--

CREATE TABLE public.users (
    did text NOT NULL,
    handle text,
    status boolean,
    pds text,
    created_date timestamp with time zone
);


ALTER TABLE public.users OWNER TO clearskyprod_user;

--
-- Name: api api_pkey; Type: CONSTRAINT; Schema: public; Owner: clearskyprod_user
--

ALTER TABLE ONLY public.api
    ADD CONSTRAINT api_pkey PRIMARY KEY (key);


--
-- Name: block_temporary_table block_temporary_table_pkey; Type: CONSTRAINT; Schema: public; Owner: clearskyprod_user
--

ALTER TABLE ONLY public.block_temporary_table
    ADD CONSTRAINT block_temporary_table_pkey PRIMARY KEY (last_processed_did);


--
-- Name: last_did_created_date last_did_created_date_pkey; Type: CONSTRAINT; Schema: public; Owner: clearskyprod_user
--

ALTER TABLE ONLY public.last_did_created_date
    ADD CONSTRAINT last_did_created_date_pkey PRIMARY KEY (last_created);


--
-- Name: mutelists mutelists_pkey; Type: CONSTRAINT; Schema: public; Owner: clearskyprod_user
--

ALTER TABLE ONLY public.mutelists
    ADD CONSTRAINT mutelists_pkey PRIMARY KEY (uri);


--
-- Name: user_prefixes user_prefixes_pkey; Type: CONSTRAINT; Schema: public; Owner: clearskyprod_user
--

ALTER TABLE ONLY public.user_prefixes
    ADD CONSTRAINT user_prefixes_pkey PRIMARY KEY (handle);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: clearskyprod_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (did);


--
-- Name: blocklist_blocked_did; Type: INDEX; Schema: public; Owner: clearskyprod_user
--

CREATE INDEX blocklist_blocked_did ON public.blocklists USING btree (blocked_did);


--
-- Name: blocklist_user_did; Type: INDEX; Schema: public; Owner: clearskyprod_user
--

CREATE INDEX blocklist_user_did ON public.blocklists USING btree (user_did);


--
-- Name: idx_user_prefixes_prefix1; Type: INDEX; Schema: public; Owner: clearskyprod_user
--

CREATE INDEX idx_user_prefixes_prefix1 ON public.user_prefixes USING btree (prefix1);


--
-- Name: idx_user_prefixes_prefix2; Type: INDEX; Schema: public; Owner: clearskyprod_user
--

CREATE INDEX idx_user_prefixes_prefix2 ON public.user_prefixes USING btree (prefix2);


--
-- Name: idx_user_prefixes_prefix3; Type: INDEX; Schema: public; Owner: clearskyprod_user
--

CREATE INDEX idx_user_prefixes_prefix3 ON public.user_prefixes USING btree (prefix3);


--
-- Name: TABLE pg_stat_database; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_database TO datadog;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON SEQUENCES  TO clearskyprod_user;


--
-- Name: DEFAULT PRIVILEGES FOR TYPES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON TYPES  TO clearskyprod_user;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON FUNCTIONS  TO clearskyprod_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON TABLES  TO clearskyprod_user;


--
-- PostgreSQL database dump complete
--

