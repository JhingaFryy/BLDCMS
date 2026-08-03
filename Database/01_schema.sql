--
-- PostgreSQL database dump
--

\restrict k2Hr3WS2voBfcKuSwKIgb316GcTjc4zWoAi9dYo7IfT8ctzrBTfmJ97nDGcJ3ke

-- Dumped from database version 18.4 (Ubuntu 18.4-0ubuntu0.26.04.1)
-- Dumped by pg_dump version 18.4 (Ubuntu 18.4-0ubuntu0.26.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- Name: activity_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.activity_logs (
    id integer NOT NULL,
    action character varying(50) NOT NULL,
    entity_type character varying(50),
    entity_id integer,
    user_id integer,
    section_id integer,
    description text,
    old_value json,
    new_value json,
    activity_metadata json,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: activity_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.activity_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: activity_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.activity_logs_id_seq OWNED BY public.activity_logs.id;


--
-- Name: checksheet_header; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.checksheet_header (
    id integer NOT NULL,
    locomotive_id integer NOT NULL,
    section_id integer NOT NULL,
    equipment_id integer,
    template_id integer NOT NULL,
    technician_mobile character varying(15) NOT NULL,
    work_type character varying(20),
    status character varying(20) DEFAULT 'DRAFT'::character varying NOT NULL,
    submitted_at timestamp without time zone,
    supervisor_mobile character varying(15),
    approved_at timestamp without time zone,
    pdf_path text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    submitted_by integer,
    approved_by integer,
    rejected_at timestamp without time zone,
    rejected_by integer,
    rejection_reason text,
    last_modified_at timestamp without time zone,
    last_modified_by integer,
    traction_motor_number character varying(20),
    maintenance_type character varying(20)
);


--
-- Name: checksheet_header_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.checksheet_header_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: checksheet_header_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.checksheet_header_id_seq OWNED BY public.checksheet_header.id;


--
-- Name: checksheet_templates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.checksheet_templates (
    id integer NOT NULL,
    equipment_id integer,
    technology character varying(20) NOT NULL,
    template_name character varying(100) NOT NULL,
    description text,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    version integer DEFAULT 1,
    template_code character varying(50) NOT NULL,
    section_id integer,
    maintenance_type character varying(20)
);


--
-- Name: checksheet_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.checksheet_templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: checksheet_templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.checksheet_templates_id_seq OWNED BY public.checksheet_templates.id;


--
-- Name: checksheet_value; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.checksheet_value (
    id integer NOT NULL,
    checksheet_id integer NOT NULL,
    field_id integer NOT NULL,
    field_value text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: checksheet_value_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.checksheet_value_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: checksheet_value_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.checksheet_value_id_seq OWNED BY public.checksheet_value.id;


--
-- Name: device_info; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.device_info (
    id integer NOT NULL,
    device_id character varying(100) NOT NULL,
    user_id integer,
    manufacturer character varying(100),
    device_model character varying(100),
    os_version character varying(50),
    app_version character varying(50),
    battery_level integer,
    network_type character varying(20),
    storage_free_mb integer,
    storage_total_mb integer,
    disclosure_acknowledged_at timestamp without time zone,
    pending_command character varying(50),
    pending_command_issued_at timestamp without time zone,
    last_seen_at timestamp without time zone DEFAULT now() NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: device_info_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.device_info_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: device_info_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.device_info_id_seq OWNED BY public.device_info.id;


--
-- Name: digital_signatures; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.digital_signatures (
    id integer NOT NULL,
    checksheet_id integer NOT NULL,
    supervisor_id integer,
    supervisor_name character varying(100) NOT NULL,
    supervisor_employee_id character varying(20) NOT NULL,
    certificate_subject text NOT NULL,
    certificate_issuer text NOT NULL,
    certificate_serial_number character varying(100) NOT NULL,
    certificate_thumbprint character varying(128) NOT NULL,
    certificate_valid_from timestamp without time zone NOT NULL,
    certificate_valid_to timestamp without time zone NOT NULL,
    signing_timestamp timestamp without time zone NOT NULL,
    signature_hash character varying(128) NOT NULL,
    verification_status character varying(30) NOT NULL,
    provider character varying(30) NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: digital_signatures_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.digital_signatures_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: digital_signatures_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.digital_signatures_id_seq OWNED BY public.digital_signatures.id;


--
-- Name: equipment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.equipment (
    id integer NOT NULL,
    equipment_code character varying(20) NOT NULL,
    equipment_name character varying(100) NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: equipment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.equipment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: equipment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.equipment_id_seq OWNED BY public.equipment.id;


--
-- Name: equipment_templates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.equipment_templates (
    id integer NOT NULL,
    equipment_id integer NOT NULL,
    template_name character varying(100) NOT NULL,
    version integer DEFAULT 1,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: equipment_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.equipment_templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: equipment_templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.equipment_templates_id_seq OWNED BY public.equipment_templates.id;


--
-- Name: locomotives; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.locomotives (
    id integer NOT NULL,
    loco_number character varying(10) NOT NULL,
    loco_model character varying(20) NOT NULL,
    technology character varying(20) NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: locomotives_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.locomotives_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: locomotives_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.locomotives_id_seq OWNED BY public.locomotives.id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    user_id integer NOT NULL,
    title character varying(255) NOT NULL,
    message text NOT NULL,
    type character varying(50) NOT NULL,
    checksheet_id integer,
    is_read boolean NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: otp_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.otp_logs (
    id integer NOT NULL,
    user_id integer NOT NULL,
    otp character varying(64) NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    is_verified boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    attempts integer DEFAULT 0 NOT NULL,
    plain_otp character varying(10)
);


--
-- Name: otp_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.otp_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: otp_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.otp_logs_id_seq OWNED BY public.otp_logs.id;


--
-- Name: section_equipment_map; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.section_equipment_map (
    id integer NOT NULL,
    section_id integer NOT NULL,
    equipment_id integer NOT NULL,
    technology character varying(20) NOT NULL,
    is_active boolean DEFAULT true
);


--
-- Name: section_equipment_map_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.section_equipment_map_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: section_equipment_map_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.section_equipment_map_id_seq OWNED BY public.section_equipment_map.id;


--
-- Name: sections; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sections (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: sections_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sections_id_seq OWNED BY public.sections.id;


--
-- Name: system_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.system_settings (
    id integer NOT NULL,
    key character varying(100) CONSTRAINT system_settings_setting_key_not_null NOT NULL,
    value text,
    category character varying(50) NOT NULL,
    description text,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: system_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.system_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: system_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.system_settings_id_seq OWNED BY public.system_settings.id;


--
-- Name: template_fields; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.template_fields (
    id integer NOT NULL,
    template_id integer NOT NULL,
    field_key character varying(100) NOT NULL,
    field_label character varying(255) NOT NULL,
    field_type character varying(30) NOT NULL,
    display_order integer NOT NULL,
    required boolean DEFAULT true,
    unit character varying(30),
    default_value text,
    options text,
    help_text text,
    is_active boolean DEFAULT true,
    min_value double precision,
    max_value double precision,
    decimal_precision integer,
    standard_value text,
    authority_reference character varying(255),
    parent_field_id integer,
    page_number integer DEFAULT 1 NOT NULL,
    is_deleted boolean DEFAULT false NOT NULL,
    deleted_at timestamp without time zone,
    validation_rule character varying(50),
    validation_threshold double precision,
    negative_values text
);


--
-- Name: template_fields_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.template_fields_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: template_fields_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.template_fields_id_seq OWNED BY public.template_fields.id;


--
-- Name: user_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_sessions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    jti character varying(36) NOT NULL,
    device_type character varying(20) NOT NULL,
    device_name character varying(100),
    ip_address character varying(45),
    user_agent character varying(500),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    last_activity timestamp without time zone DEFAULT now() NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    revoked boolean NOT NULL,
    refresh_token_hash text,
    device_id character varying(255),
    app_version character varying(50),
    revoked_at timestamp without time zone,
    revoked_reason text
);


--
-- Name: user_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_sessions_id_seq OWNED BY public.user_sessions.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    employee_id character varying(20) NOT NULL,
    name character varying(100) NOT NULL,
    mobile character varying(10) NOT NULL,
    email character varying(100),
    password_hash character varying(255),
    role character varying(20) NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    section_id integer
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: activity_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.activity_logs ALTER COLUMN id SET DEFAULT nextval('public.activity_logs_id_seq'::regclass);


--
-- Name: checksheet_header id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checksheet_header ALTER COLUMN id SET DEFAULT nextval('public.checksheet_header_id_seq'::regclass);


--
-- Name: checksheet_templates id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checksheet_templates ALTER COLUMN id SET DEFAULT nextval('public.checksheet_templates_id_seq'::regclass);


--
-- Name: checksheet_value id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checksheet_value ALTER COLUMN id SET DEFAULT nextval('public.checksheet_value_id_seq'::regclass);


--
-- Name: device_info id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_info ALTER COLUMN id SET DEFAULT nextval('public.device_info_id_seq'::regclass);


--
-- Name: digital_signatures id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.digital_signatures ALTER COLUMN id SET DEFAULT nextval('public.digital_signatures_id_seq'::regclass);


--
-- Name: equipment id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment ALTER COLUMN id SET DEFAULT nextval('public.equipment_id_seq'::regclass);


--
-- Name: equipment_templates id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment_templates ALTER COLUMN id SET DEFAULT nextval('public.equipment_templates_id_seq'::regclass);


--
-- Name: locomotives id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locomotives ALTER COLUMN id SET DEFAULT nextval('public.locomotives_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- Name: otp_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.otp_logs ALTER COLUMN id SET DEFAULT nextval('public.otp_logs_id_seq'::regclass);


--
-- Name: section_equipment_map id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.section_equipment_map ALTER COLUMN id SET DEFAULT nextval('public.section_equipment_map_id_seq'::regclass);


--
-- Name: sections id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sections ALTER COLUMN id SET DEFAULT nextval('public.sections_id_seq'::regclass);


--
-- Name: system_settings id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_settings ALTER COLUMN id SET DEFAULT nextval('public.system_settings_id_seq'::regclass);


--
-- Name: template_fields id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.template_fields ALTER COLUMN id SET DEFAULT nextval('public.template_fields_id_seq'::regclass);


--
-- Name: user_sessions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_sessions ALTER COLUMN id SET DEFAULT nextval('public.user_sessions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: activity_logs activity_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_pkey PRIMARY KEY (id);


--
-- Name: checksheet_header checksheet_header_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checksheet_header
    ADD CONSTRAINT checksheet_header_pkey PRIMARY KEY (id);


--
-- Name: checksheet_templates checksheet_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checksheet_templates
    ADD CONSTRAINT checksheet_templates_pkey PRIMARY KEY (id);


--
-- Name: checksheet_value checksheet_value_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checksheet_value
    ADD CONSTRAINT checksheet_value_pkey PRIMARY KEY (id);


--
-- Name: device_info device_info_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_info
    ADD CONSTRAINT device_info_pkey PRIMARY KEY (id);


--
-- Name: digital_signatures digital_signatures_checksheet_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.digital_signatures
    ADD CONSTRAINT digital_signatures_checksheet_id_key UNIQUE (checksheet_id);


--
-- Name: digital_signatures digital_signatures_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.digital_signatures
    ADD CONSTRAINT digital_signatures_pkey PRIMARY KEY (id);


--
-- Name: equipment equipment_equipment_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_equipment_code_key UNIQUE (equipment_code);


--
-- Name: equipment equipment_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_pkey PRIMARY KEY (id);


--
-- Name: equipment_templates equipment_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment_templates
    ADD CONSTRAINT equipment_templates_pkey PRIMARY KEY (id);


--
-- Name: locomotives locomotives_loco_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locomotives
    ADD CONSTRAINT locomotives_loco_number_key UNIQUE (loco_number);


--
-- Name: locomotives locomotives_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locomotives
    ADD CONSTRAINT locomotives_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: otp_logs otp_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.otp_logs
    ADD CONSTRAINT otp_logs_pkey PRIMARY KEY (id);


--
-- Name: section_equipment_map section_equipment_map_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.section_equipment_map
    ADD CONSTRAINT section_equipment_map_pkey PRIMARY KEY (id);


--
-- Name: sections sections_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_name_key UNIQUE (name);


--
-- Name: sections sections_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_pkey PRIMARY KEY (id);


--
-- Name: system_settings system_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT system_settings_pkey PRIMARY KEY (id);


--
-- Name: system_settings system_settings_setting_key_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT system_settings_setting_key_key UNIQUE (key);


--
-- Name: template_fields template_fields_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.template_fields
    ADD CONSTRAINT template_fields_pkey PRIMARY KEY (id);


--
-- Name: system_settings uq_system_settings_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT uq_system_settings_key UNIQUE (key);


--
-- Name: checksheet_templates uq_template_code_version; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checksheet_templates
    ADD CONSTRAINT uq_template_code_version UNIQUE (template_code, version);


--
-- Name: user_sessions user_sessions_jti_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_jti_key UNIQUE (jti);


--
-- Name: user_sessions user_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_pkey PRIMARY KEY (id);


--
-- Name: users users_employee_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_employee_id_key UNIQUE (employee_id);


--
-- Name: users users_mobile_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_mobile_key UNIQUE (mobile);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_activity_logs_action; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_activity_logs_action ON public.activity_logs USING btree (action);


--
-- Name: ix_activity_logs_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_activity_logs_created_at ON public.activity_logs USING btree (created_at);


--
-- Name: ix_activity_logs_entity_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_activity_logs_entity_id ON public.activity_logs USING btree (entity_id);


--
-- Name: ix_activity_logs_entity_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_activity_logs_entity_type ON public.activity_logs USING btree (entity_type);


--
-- Name: ix_activity_logs_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_activity_logs_id ON public.activity_logs USING btree (id);


--
-- Name: ix_activity_logs_section_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_activity_logs_section_id ON public.activity_logs USING btree (section_id);


--
-- Name: ix_activity_logs_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_activity_logs_user_id ON public.activity_logs USING btree (user_id);


--
-- Name: ix_checksheet_header_equipment_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_checksheet_header_equipment_id ON public.checksheet_header USING btree (equipment_id);


--
-- Name: ix_checksheet_header_locomotive_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_checksheet_header_locomotive_id ON public.checksheet_header USING btree (locomotive_id);


--
-- Name: ix_checksheet_header_section_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_checksheet_header_section_id ON public.checksheet_header USING btree (section_id);


--
-- Name: ix_checksheet_header_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_checksheet_header_status ON public.checksheet_header USING btree (status);


--
-- Name: ix_checksheet_header_submitted_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_checksheet_header_submitted_at ON public.checksheet_header USING btree (submitted_at);


--
-- Name: ix_checksheet_header_technician_mobile; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_checksheet_header_technician_mobile ON public.checksheet_header USING btree (technician_mobile);


--
-- Name: ix_checksheet_templates_section_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_checksheet_templates_section_id ON public.checksheet_templates USING btree (section_id);


--
-- Name: ix_checksheet_value_checksheet_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_checksheet_value_checksheet_id ON public.checksheet_value USING btree (checksheet_id);


--
-- Name: ix_checksheet_value_field_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_checksheet_value_field_id ON public.checksheet_value USING btree (field_id);


--
-- Name: ix_device_info_device_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_device_info_device_id ON public.device_info USING btree (device_id);


--
-- Name: ix_device_info_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_device_info_id ON public.device_info USING btree (id);


--
-- Name: ix_device_info_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_device_info_user_id ON public.device_info USING btree (user_id);


--
-- Name: ix_digital_signatures_checksheet_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_digital_signatures_checksheet_id ON public.digital_signatures USING btree (checksheet_id);


--
-- Name: ix_digital_signatures_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_digital_signatures_id ON public.digital_signatures USING btree (id);


--
-- Name: ix_digital_signatures_signing_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_digital_signatures_signing_timestamp ON public.digital_signatures USING btree (signing_timestamp);


--
-- Name: ix_notifications_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_notifications_id ON public.notifications USING btree (id);


--
-- Name: ix_notifications_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_notifications_user_id ON public.notifications USING btree (user_id);


--
-- Name: ix_otp_logs_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_otp_logs_id ON public.otp_logs USING btree (id);


--
-- Name: ix_template_fields_is_deleted; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_template_fields_is_deleted ON public.template_fields USING btree (is_deleted);


--
-- Name: ix_template_fields_page_number; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_template_fields_page_number ON public.template_fields USING btree (page_number);


--
-- Name: ix_template_fields_parent_field_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_template_fields_parent_field_id ON public.template_fields USING btree (parent_field_id);


--
-- Name: ix_user_sessions_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_sessions_id ON public.user_sessions USING btree (id);


--
-- Name: ix_user_sessions_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_sessions_user_id ON public.user_sessions USING btree (user_id);


--
-- Name: activity_logs activity_logs_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id);


--
-- Name: activity_logs activity_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: checksheet_header checksheet_header_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checksheet_header
    ADD CONSTRAINT checksheet_header_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(id);


--
-- Name: checksheet_header checksheet_header_locomotive_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checksheet_header
    ADD CONSTRAINT checksheet_header_locomotive_id_fkey FOREIGN KEY (locomotive_id) REFERENCES public.locomotives(id);


--
-- Name: checksheet_header checksheet_header_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checksheet_header
    ADD CONSTRAINT checksheet_header_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id);


--
-- Name: checksheet_header checksheet_header_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checksheet_header
    ADD CONSTRAINT checksheet_header_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.checksheet_templates(id);


--
-- Name: checksheet_templates checksheet_templates_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checksheet_templates
    ADD CONSTRAINT checksheet_templates_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(id);


--
-- Name: checksheet_templates checksheet_templates_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checksheet_templates
    ADD CONSTRAINT checksheet_templates_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id);


--
-- Name: checksheet_value checksheet_value_checksheet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checksheet_value
    ADD CONSTRAINT checksheet_value_checksheet_id_fkey FOREIGN KEY (checksheet_id) REFERENCES public.checksheet_header(id) ON DELETE CASCADE;


--
-- Name: checksheet_value checksheet_value_field_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checksheet_value
    ADD CONSTRAINT checksheet_value_field_id_fkey FOREIGN KEY (field_id) REFERENCES public.template_fields(id);


--
-- Name: device_info device_info_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_info
    ADD CONSTRAINT device_info_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: digital_signatures digital_signatures_checksheet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.digital_signatures
    ADD CONSTRAINT digital_signatures_checksheet_id_fkey FOREIGN KEY (checksheet_id) REFERENCES public.checksheet_header(id) ON DELETE CASCADE;


--
-- Name: digital_signatures digital_signatures_supervisor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.digital_signatures
    ADD CONSTRAINT digital_signatures_supervisor_id_fkey FOREIGN KEY (supervisor_id) REFERENCES public.users(id);


--
-- Name: equipment_templates equipment_templates_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment_templates
    ADD CONSTRAINT equipment_templates_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(id);


--
-- Name: checksheet_header fk_checksheet_header_approved_by; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checksheet_header
    ADD CONSTRAINT fk_checksheet_header_approved_by FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: checksheet_header fk_checksheet_header_last_modified_by; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checksheet_header
    ADD CONSTRAINT fk_checksheet_header_last_modified_by FOREIGN KEY (last_modified_by) REFERENCES public.users(id);


--
-- Name: checksheet_header fk_checksheet_header_rejected_by; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checksheet_header
    ADD CONSTRAINT fk_checksheet_header_rejected_by FOREIGN KEY (rejected_by) REFERENCES public.users(id);


--
-- Name: checksheet_header fk_checksheet_header_submitted_by; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checksheet_header
    ADD CONSTRAINT fk_checksheet_header_submitted_by FOREIGN KEY (submitted_by) REFERENCES public.users(id);


--
-- Name: notifications notifications_checksheet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_checksheet_id_fkey FOREIGN KEY (checksheet_id) REFERENCES public.checksheet_header(id);


--
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: otp_logs otp_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.otp_logs
    ADD CONSTRAINT otp_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: section_equipment_map section_equipment_map_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.section_equipment_map
    ADD CONSTRAINT section_equipment_map_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(id);


--
-- Name: section_equipment_map section_equipment_map_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.section_equipment_map
    ADD CONSTRAINT section_equipment_map_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id);


--
-- Name: template_fields template_fields_parent_field_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.template_fields
    ADD CONSTRAINT template_fields_parent_field_id_fkey FOREIGN KEY (parent_field_id) REFERENCES public.template_fields(id);


--
-- Name: template_fields template_fields_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.template_fields
    ADD CONSTRAINT template_fields_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.checksheet_templates(id) ON DELETE CASCADE;


--
-- Name: user_sessions user_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users users_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id);


--
-- PostgreSQL database dump complete
--

\unrestrict k2Hr3WS2voBfcKuSwKIgb316GcTjc4zWoAi9dYo7IfT8ctzrBTfmJ97nDGcJ3ke

