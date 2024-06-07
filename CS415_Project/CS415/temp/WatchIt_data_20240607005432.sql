--
-- PostgreSQL database dump
--

-- Dumped from database version 16.2
-- Dumped by pg_dump version 16.2

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
-- Data for Name: WatchIt_cinemahall; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public."WatchIt_cinemahall" (id, cinema_type, num_rows, num_cols, adult_price, child_price) FROM stdin;
3	Premium	9	9	10.00	8.00
2	Deluxe	11	11	11.00	9.00
1	Standard	5	5	7.50	2.50
4	Vx	10	10	15.00	10.00
5	Test Type	5	5	\N	\N
6	Test Type	5	5	\N	\N
7	Test again	10	10	\N	\N
\.


--
-- Data for Name: WatchIt_movie; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public."WatchIt_movie" (id, title, description, duration, starring, director, release_date, language, "ageRating", image, trailer) FROM stdin;
5	testing db	gonna delete this	123	me	me	2024-06-29	English	PG-13	movie_images/bnr-Improving_Canadas_Biodiversity_with_Terrestrial_Offsets.jpg	https://youtu.be/ByAn8DF8Ykk
2	Abigail	After a group of criminals kidnap the ballerina daughter of a powerful underworld figure, they retreat to an isolated mansion, unaware that they're locked inside with no normal little girl.	149	Melissa Barrera - Joey\r\nDan Stevens - Frank\r\nAlisha Weir - Abigail\r\nWilliam Catlett - Rickles (as Will Catlett)\r\nKathryn Newton - Sammy\r\nKevin Durand - Peter\r\nAngus Cloud - Dean\r\nGiancarlo Esposito - Lambert\r\nMatthew Goode - Father	Matt Bettinelli-Olpin\t\r\nTyler Gillett	2024-05-25	English	R	movie_images/Abigail_WZgAyUe.jpeg	https://youtu.be/ByAn8DF8Ykk
3	new movie	ffffffff	100	gWRRggggggggggggggg	nnnnnnnnnnnnnnnnnnnnnnnnnnnn	2024-05-29	English	PG-13	movie_images/deadpool_qo1iZKd.jpg	https://youtu.be/ByAn8DF8Ykk
1	The Garfield Movie	Garfield (voiced by Chris Pratt), the world-famous, Monday-hating, lasagna-loving indoor cat, is about to have a wild outdoor adventure! After an unexpected reunion with his long-lost father – scruffy street cat Vic (voiced by Samuel L. Jackson) – Garfield and his canine friend Odie are forced from their perfectly pampered life into joining Vic in a hilarious, high-stakes heist.	101	Garfield (voiced by Chris Pratt), the world-famous, Monday-hating, lasagna-loving indoor cat, is about to have a wild outdoor adventure! After an unexpected reunion with his long-lost father – scruffy street cat Vic (voiced by Samuel L. Jackson) – Garfield and his canine friend Odie are forced from their perfectly pampered life into joining Vic in a hilarious, high-stakes heist.	Mark Dindal	2024-05-20	English	G	movie_images/Garfield_nwtxCJF.jpeg	https://youtu.be/ByAn8DF8Ykk
\.


--
-- Data for Name: WatchIt_showtime; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public."WatchIt_showtime" (id, showtime, seats_generated, cinema_hall_id, movie_id) FROM stdin;
12	2024-06-16 23:48:00+12	t	4	2
11	2024-06-07 10:06:00+12	f	2	3
\.


--
-- Data for Name: WatchIt_user; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public."WatchIt_user" (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_email_verified, secret_key, user_phone) FROM stdin;
1	pbkdf2_sha256$600000$7KurqkpU2cTEUBCcc8XTm8$9B/YUhGkFPqPTkYcK/cZCoRphJdoG3YgeiB3LikVdiM=	2024-06-04 17:11:29.385137+12	t	karan			karan@gmail.com	t	t	2024-06-04 17:10:56.216697+12	f	\N	\N
\.


--
-- Data for Name: WatchIt_booking; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public."WatchIt_booking" (id, booking_date, payment_amount, num_seats, edited, charge_id, card_last4, cinema_hall_id, movie_id, showtime_id, user_id) FROM stdin;
34	2024-06-04 14:17:40.88075+12	60.00	6	f	pi_3PNmwQDGr86VR9Mc04hbTxGs	4242	2	3	11	1
38	2024-06-04 17:25:39.287085+12	11.00	1	f	pi_3PNpsMDGr86VR9Mc1nVimCTG	4242	2	3	11	1
\.


--
-- Data for Name: WatchIt_seat; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public."WatchIt_seat" (id, seat_label, availability, showtime_id) FROM stdin;
631	B3	t	11
632	B4	t	11
633	B5	t	11
634	C1	t	11
635	C2	t	11
636	C3	t	11
637	C4	t	11
638	C5	t	11
639	D1	t	11
640	D2	t	11
641	D3	t	11
642	D4	t	11
643	D5	t	11
644	E1	t	11
645	E2	t	11
646	E3	t	11
647	E4	t	11
648	E5	t	11
1124	J10	f	12
1112	I8	t	12
1113	I9	t	12
1114	I10	t	12
1115	J1	t	12
1116	J2	t	12
1117	J3	t	12
1118	J4	t	12
1119	J5	t	12
1120	J6	t	12
1121	J7	t	12
1122	J8	t	12
1123	J9	t	12
1025	A1	t	12
1026	A2	t	12
1027	A3	t	12
1028	A4	t	12
1029	A5	t	12
1030	A6	t	12
1031	A7	t	12
1032	A8	t	12
1033	A9	t	12
1034	A10	t	12
1035	B1	t	12
1036	B2	t	12
1037	B3	t	12
1038	B4	t	12
1039	B5	t	12
1040	B6	t	12
1041	B7	t	12
1042	B8	t	12
1043	B9	t	12
1044	B10	t	12
1045	C1	t	12
1046	C2	t	12
1047	C3	t	12
1048	C4	t	12
1049	C5	t	12
1050	C6	t	12
1051	C7	t	12
1052	C8	t	12
1053	C9	t	12
1054	C10	t	12
1055	D1	t	12
1056	D2	t	12
1057	D3	t	12
1058	D4	t	12
1059	D5	t	12
1060	D6	t	12
1061	D7	t	12
1062	D8	t	12
1063	D9	t	12
1064	D10	t	12
1065	E1	t	12
1066	E2	t	12
1067	E3	t	12
1068	E4	t	12
1069	E5	t	12
1070	E6	t	12
1071	E7	t	12
1072	E8	t	12
1073	E9	t	12
1074	E10	t	12
1075	F1	t	12
1076	F2	t	12
1077	F3	t	12
1078	F4	t	12
1079	F5	t	12
1080	F6	t	12
1081	F7	t	12
1082	F8	t	12
1083	F9	t	12
1084	F10	t	12
1085	G1	t	12
1086	G2	t	12
1087	G3	t	12
1088	G4	t	12
1089	G5	t	12
1090	G6	t	12
1091	G7	t	12
1092	G8	t	12
1093	G9	t	12
1094	G10	t	12
1095	H1	t	12
1096	H2	t	12
1097	H3	t	12
1098	H4	t	12
1099	H5	t	12
1100	H6	t	12
1101	H7	t	12
1102	H8	t	12
1103	H9	t	12
1104	H10	t	12
1105	I1	t	12
1106	I2	t	12
1107	I3	t	12
1108	I4	t	12
1109	I5	t	12
1110	I6	t	12
1111	I7	t	12
630	B2	t	11
624	A1	f	11
625	A2	f	11
626	A3	f	11
627	A4	f	11
628	A5	f	11
629	B1	f	11
\.


--
-- Data for Name: WatchIt_booking_seats; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public."WatchIt_booking_seats" (id, booking_id, seat_id) FROM stdin;
98	34	624
99	34	625
100	34	626
101	34	627
102	34	628
103	34	629
113	38	630
\.


--
-- Data for Name: WatchIt_deals; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public."WatchIt_deals" (id, "Meal", "Price", description, image) FROM stdin;
\.


--
-- Data for Name: WatchIt_feedback; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public."WatchIt_feedback" (id, subject, feedback, file, created_at, approved, reviewed, user_id) FROM stdin;
1	Change seats	ddddddddddddd	feedback_files/My_Photo_6nvL1H7.jpg	2024-06-04 17:18:31+12	t	f	1
\.


--
-- Data for Name: WatchIt_tag; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public."WatchIt_tag" (id, name) FROM stdin;
1	Action
3	Animation
4	Children's Film
5	Comedy
6	Adventure
7	Family Film
8	Fantasy
9	Slapstick
10	Horror
\.


--
-- Data for Name: WatchIt_movie_tags; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public."WatchIt_movie_tags" (id, movie_id, tag_id) FROM stdin;
3	1	3
4	1	4
5	1	5
6	1	6
7	1	7
8	1	8
9	1	9
10	2	10
11	3	1
12	3	4
13	5	8
\.


--
-- Data for Name: WatchIt_passwordresettoken; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public."WatchIt_passwordresettoken" (id, token, created_at, used, user_id) FROM stdin;
\.


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public.auth_group (id, name) FROM stdin;
1	Admin
\.


--
-- Data for Name: WatchIt_user_groups; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public."WatchIt_user_groups" (id, user_id, group_id) FROM stdin;
1	1	1
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	WatchIt	cinemahall
2	WatchIt	deals
3	WatchIt	movie
4	WatchIt	tag
5	WatchIt	user
6	WatchIt	showtime
7	WatchIt	seat
8	WatchIt	passwordresettoken
9	WatchIt	feedback
10	WatchIt	booking
11	admin	logentry
12	auth	permission
13	auth	group
14	contenttypes	contenttype
15	sessions	session
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add cinema hall	1	add_cinemahall
2	Can change cinema hall	1	change_cinemahall
3	Can delete cinema hall	1	delete_cinemahall
4	Can view cinema hall	1	view_cinemahall
5	Can add deals	2	add_deals
6	Can change deals	2	change_deals
7	Can delete deals	2	delete_deals
8	Can view deals	2	view_deals
9	Can add movie	3	add_movie
10	Can change movie	3	change_movie
11	Can delete movie	3	delete_movie
12	Can view movie	3	view_movie
13	Can add tag	4	add_tag
14	Can change tag	4	change_tag
15	Can delete tag	4	delete_tag
16	Can view tag	4	view_tag
17	Can add user	5	add_user
18	Can change user	5	change_user
19	Can delete user	5	delete_user
20	Can view user	5	view_user
21	Can add showtime	6	add_showtime
22	Can change showtime	6	change_showtime
23	Can delete showtime	6	delete_showtime
24	Can view showtime	6	view_showtime
25	Can add seat	7	add_seat
26	Can change seat	7	change_seat
27	Can delete seat	7	delete_seat
28	Can view seat	7	view_seat
29	Can add password reset token	8	add_passwordresettoken
30	Can change password reset token	8	change_passwordresettoken
31	Can delete password reset token	8	delete_passwordresettoken
32	Can view password reset token	8	view_passwordresettoken
33	Can add feedback	9	add_feedback
34	Can change feedback	9	change_feedback
35	Can delete feedback	9	delete_feedback
36	Can view feedback	9	view_feedback
37	Can add booking	10	add_booking
38	Can change booking	10	change_booking
39	Can delete booking	10	delete_booking
40	Can view booking	10	view_booking
41	Can add log entry	11	add_logentry
42	Can change log entry	11	change_logentry
43	Can delete log entry	11	delete_logentry
44	Can view log entry	11	view_logentry
45	Can add permission	12	add_permission
46	Can change permission	12	change_permission
47	Can delete permission	12	delete_permission
48	Can view permission	12	view_permission
49	Can add group	13	add_group
50	Can change group	13	change_group
51	Can delete group	13	delete_group
52	Can view group	13	view_group
53	Can add content type	14	add_contenttype
54	Can change content type	14	change_contenttype
55	Can delete content type	14	delete_contenttype
56	Can view content type	14	view_contenttype
57	Can add session	15	add_session
58	Can change session	15	change_session
59	Can delete session	15	delete_session
60	Can view session	15	view_session
\.


--
-- Data for Name: WatchIt_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public."WatchIt_user_user_permissions" (id, user_id, permission_id) FROM stdin;
1	1	1
2	1	2
3	1	3
4	1	4
5	1	5
6	1	6
7	1	7
8	1	8
9	1	9
10	1	10
11	1	11
12	1	12
13	1	13
14	1	14
15	1	15
16	1	16
17	1	17
18	1	18
19	1	19
20	1	20
21	1	21
22	1	22
23	1	23
24	1	24
25	1	25
26	1	26
27	1	27
28	1	28
29	1	29
30	1	30
31	1	31
32	1	32
33	1	33
34	1	34
35	1	35
36	1	36
37	1	37
38	1	38
39	1	39
40	1	40
41	1	46
42	1	47
43	1	48
44	1	53
45	1	54
46	1	55
47	1	56
48	1	57
49	1	58
50	1	59
51	1	60
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
1	1	1
2	1	2
3	1	3
4	1	4
5	1	5
6	1	6
7	1	7
8	1	8
9	1	9
10	1	10
11	1	11
12	1	12
13	1	13
14	1	14
15	1	15
16	1	16
17	1	17
18	1	18
19	1	19
20	1	20
21	1	21
22	1	22
23	1	23
24	1	24
25	1	25
26	1	26
27	1	27
28	1	28
29	1	29
30	1	30
31	1	31
32	1	32
33	1	33
34	1	34
35	1	35
36	1	36
37	1	37
38	1	38
39	1	39
40	1	40
41	1	41
42	1	42
43	1	43
44	1	44
45	1	45
46	1	46
47	1	47
48	1	48
49	1	49
50	1	50
51	1	51
52	1	52
53	1	53
54	1	54
55	1	55
56	1	56
57	1	57
58	1	58
59	1	59
60	1	60
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2024-06-04 17:18:41.704286+12	1	Change seats	2	[{"changed": {"fields": ["Approved"]}}]	9	1
120	2024-06-04 17:26:14.510388+12	38	Booking for new movie on 2024-06-04 05:25:39.287085+00:00	3		10	1
121	2024-06-06 19:29:35.488491+12	34	Booking for new movie on 2024-06-04 02:17:40.880750+00:00	3		10	1
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2024-06-04 17:10:15.526876+12
2	contenttypes	0002_remove_content_type_name	2024-06-04 17:10:15.546925+12
3	auth	0001_initial	2024-06-04 17:10:15.692339+12
4	auth	0002_alter_permission_name_max_length	2024-06-04 17:10:15.702721+12
5	auth	0003_alter_user_email_max_length	2024-06-04 17:10:15.716276+12
6	auth	0004_alter_user_username_opts	2024-06-04 17:10:15.730805+12
7	auth	0005_alter_user_last_login_null	2024-06-04 17:10:15.74729+12
8	auth	0006_require_contenttypes_0002	2024-06-04 17:10:15.755316+12
9	auth	0007_alter_validators_add_error_messages	2024-06-04 17:10:15.774319+12
10	auth	0008_alter_user_username_max_length	2024-06-04 17:10:15.791678+12
11	auth	0009_alter_user_last_name_max_length	2024-06-04 17:10:15.811074+12
12	auth	0010_alter_group_name_max_length	2024-06-04 17:10:15.837559+12
13	auth	0011_update_proxy_permissions	2024-06-04 17:10:15.856095+12
14	auth	0012_alter_user_first_name_max_length	2024-06-04 17:10:15.872696+12
15	WatchIt	0001_initial	2024-06-04 17:10:16.425554+12
16	WatchIt	0002_user_user_phone	2024-06-04 17:10:16.448474+12
17	admin	0001_initial	2024-06-04 17:10:16.533678+12
18	admin	0002_logentry_remove_auto_add	2024-06-04 17:10:16.556623+12
19	admin	0003_logentry_add_action_flag_choices	2024-06-04 17:10:16.585106+12
20	sessions	0001_initial	2024-06-04 17:10:16.631958+12
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: karan
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
s3uovtn555bsrl0xkstvrmdhj51wb0g0	.eJxVjMEOwiAQBf-FsyFAgQWP3v0GsiwgVQNJaU_Gf9cmPej1zcx7sYDbWsM28hLmxM5MstPvFpEeue0g3bHdOqfe1mWOfFf4QQe_9pSfl8P9O6g46rd2ZICEIVJakRHFFwkCorTOGZImks7KpGzRChRx0mD9JJTyBYoi6YC9P86PNxA:1sB5k3:byxlz3y1X9nufLTl7GJwbt_nrNoA94KDierzTurW_d4	2024-06-09 16:44:19.082295+12
ja1ov4iot92sooxk6rgo5ig9gqu75i4s	.eJxVjMEOwiAQBf-FsyFAgQWP3v0GsiwgVQNJaU_Gf9cmPej1zcx7sYDbWsM28hLmxM5MstPvFpEeue0g3bHdOqfe1mWOfFf4QQe_9pSfl8P9O6g46rd2ZICEIVJakRHFFwkCorTOGZImks7KpGzRChRx0mD9JJTyBYoi6YC9P86PNxA:1sCQlK:z1m4x3AuHlFA20Y_B8Jlzdinr7VFQX8n7QMpuQ1499Y	2024-06-13 09:23:10.312729+12
7t5msr3gy9eq140np6lskm4apmnazowr	.eJxVjMEOwiAQBf-FsyFAgQWP3v0GsiwgVQNJaU_Gf9cmPej1zcx7sYDbWsM28hLmxM5MstPvFpEeue0g3bHdOqfe1mWOfFf4QQe_9pSfl8P9O6g46rd2ZICEIVJakRHFFwkCorTOGZImks7KpGzRChRx0mD9JJTyBYoi6YC9P86PNxA:1sCvh6:7cUSZZoITHOoKUi8VaqL49YsuIg9UgZItJYbjRQ1GHw	2024-06-14 18:24:52.258892+12
puybsbsb3erx2k912q6mdobkk8vys6as	.eJxVjMEOwiAQBf-FsyFAgQWP3v0GsiwgVQNJaU_Gf9cmPej1zcx7sYDbWsM28hLmxM5MstPvFpEeue0g3bHdOqfe1mWOfFf4QQe_9pSfl8P9O6g46rd2ZICEIVJakRHFFwkCorTOGZImks7KpGzRChRx0mD9JJTyBYoi6YC9P86PNxA:1sCvky:YAjUbqQlJOFoCTLTRa0837IQZuqsFQGX-B4ggbzccC0	2024-06-14 18:28:52.632083+12
tn6ppwazvdad4mfy5mniwfmqbtvtd939	.eJxVjMEOwiAQBf-FsyFAgQWP3v0GsiwgVQNJaU_Gf9cmPej1zcx7sYDbWsM28hLmxM5MstPvFpEeue0g3bHdOqfe1mWOfFf4QQe_9pSfl8P9O6g46rd2ZICEIVJakRHFFwkCorTOGZImks7KpGzRChRx0mD9JJTyBYoi6YC9P86PNxA:1sCvwj:q9UMFadmlCDVZPDWlvOPg2VbJNX3dp8lSw3bzzsp8xE	2024-06-14 18:41:01.912833+12
5lroy8lrj0yizurj39m6q3l0m6go0rob	.eJxVjMEOwiAQBf-FsyFAgQWP3v0GsiwgVQNJaU_Gf9cmPej1zcx7sYDbWsM28hLmxM5MstPvFpEeue0g3bHdOqfe1mWOfFf4QQe_9pSfl8P9O6g46rd2ZICEIVJakRHFFwkCorTOGZImks7KpGzRChRx0mD9JJTyBYoi6YC9P86PNxA:1sCwd3:kbPhxUDCvzVU5mHiRky9mxzlaj_WtXr0R99xrv3kdHA	2024-06-14 19:24:45.753451+12
lf9aqwrv7vdzzo8rvlz8ylv7b66iodpo	.eJxVjMEOwiAQBf-FsyFAgQWP3v0GsiwgVQNJaU_Gf9cmPej1zcx7sYDbWsM28hLmxM5MstPvFpEeue0g3bHdOqfe1mWOfFf4QQe_9pSfl8P9O6g46rd2ZICEIVJakRHFFwkCorTOGZImks7KpGzRChRx0mD9JJTyBYoi6YC9P86PNxA:1sCwfo:hS9sdxg3FPeaqdPotxMwpPUnXBn-Mncyh3xb7MGLeQY	2024-06-14 19:27:36.068744+12
4ayui4keopzovqxvsk5cbujagnfg3wl8	.eJxVjMEOwiAQBf-FsyFAgQWP3v0GsiwgVQNJaU_Gf9cmPej1zcx7sYDbWsM28hLmxM5MstPvFpEeue0g3bHdOqfe1mWOfFf4QQe_9pSfl8P9O6g46rd2ZICEIVJakRHFFwkCorTOGZImks7KpGzRChRx0mD9JJTyBYoi6YC9P86PNxA:1sCwjJ:6sGPy-jSZClPkrbh2nfgK4EJrt0iMBZE_FU_TsO-a0o	2024-06-14 19:31:13.161041+12
qflngqlbc71yr9ir4a3kde9r38i199u2	.eJxVjMEOwiAQBf-FsyFAgQWP3v0GsiwgVQNJaU_Gf9cmPej1zcx7sYDbWsM28hLmxM5MstPvFpEeue0g3bHdOqfe1mWOfFf4QQe_9pSfl8P9O6g46rd2ZICEIVJakRHFFwkCorTOGZImks7KpGzRChRx0mD9JJTyBYoi6YC9P86PNxA:1sCwnT:O3l-3wbMyMtTl2VdeJG_BHyYWehubyYrlvAfwFWfmOY	2024-06-14 19:35:31.232321+12
dwv8wsnfnbxqyy3n9jjt0fcg7j0iicp1	.eJxVjMEOwiAQBf-FsyFAgQWP3v0GsiwgVQNJaU_Gf9cmPej1zcx7sYDbWsM28hLmxM5MstPvFpEeue0g3bHdOqfe1mWOfFf4QQe_9pSfl8P9O6g46rd2ZICEIVJakRHFFwkCorTOGZImks7KpGzRChRx0mD9JJTyBYoi6YC9P86PNxA:1sD3t6:_9XQ6QXd0QmcQakaPv-9EStyOd2lCTpgsAyZu86koUo	2024-06-15 03:09:48.934783+12
9f9omu85fo3yi899cj135zwycm0j0mpf	.eJxVj8uOwyAMRf-FdYSAhJB0Oft-AzLGSejQUAWiqqrm34dKmUeXPvf4Wn4yC3tZ7J5ps8GzE5Os-c8c4Cetr8BfYJ0Tx7SWLTj-UviRZn5OnuLH4b4VLJCXuj2gNig0ouoUajGNkzTCONkPg0apHXaktKceegHCtZ3px1YoNU5mUigHU0vB77HYEuqRktlJNQyXEP0fkQ0rqUC0ty0g1dlw_YN-pbZhd4qYrmSvlDPMZH3ItwgPql-WbaevbztQXKs:1sEL0I:pnI5e7c0fikJ0qw3liUV9uaQ8eUpRSJO-LLMWEkuofw	2024-06-18 15:38:30.870548+12
7x42d6ajwf355z7rrmbmgxr294vx8jin	.eJxVjs1uwyAQhN-Fs4UM_iXH3vsMaNldbFpiIoNVRVHePbYU1e31m29G8xAWtjLbLfNqA4mLUKL6yxzgNy9HQF-wTEliWsoanDwU-U6z_EzE8ePt_huYIc97G5UHP4zeKNCuG3scXGdgdHrwPTpD2mNbm17X2nnXcNNyZ7TShqhF1TbH6A9HTFe2V84ZJrYU8i3CnfdzZd24EkBbLLaE_UXJ4qIqgXOIdJK6EiUViPa2BuTdUPIXnbXnC02wXcQ:1sEMfk:s6k1h4fPiFOen428lqTP9R87KP0lv9jxyLhN9obnvdU	2024-06-18 17:25:24.224397+12
\.


--
-- Name: WatchIt_booking_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public."WatchIt_booking_id_seq"', 38, true);


--
-- Name: WatchIt_booking_seats_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public."WatchIt_booking_seats_id_seq"', 113, true);


--
-- Name: WatchIt_cinemahall_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public."WatchIt_cinemahall_id_seq"', 7, true);


--
-- Name: WatchIt_deals_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public."WatchIt_deals_id_seq"', 1, false);


--
-- Name: WatchIt_feedback_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public."WatchIt_feedback_id_seq"', 8, true);


--
-- Name: WatchIt_movie_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public."WatchIt_movie_id_seq"', 5, true);


--
-- Name: WatchIt_movie_tags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public."WatchIt_movie_tags_id_seq"', 13, true);


--
-- Name: WatchIt_passwordresettoken_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public."WatchIt_passwordresettoken_id_seq"', 1, false);


--
-- Name: WatchIt_seat_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public."WatchIt_seat_id_seq"', 1442, true);


--
-- Name: WatchIt_showtime_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public."WatchIt_showtime_id_seq"', 19, true);


--
-- Name: WatchIt_tag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public."WatchIt_tag_id_seq"', 10, true);


--
-- Name: WatchIt_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public."WatchIt_user_groups_id_seq"', 1, true);


--
-- Name: WatchIt_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public."WatchIt_user_id_seq"', 2, true);


--
-- Name: WatchIt_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public."WatchIt_user_user_permissions_id_seq"', 51, true);


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, true);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 60, true);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 60, true);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 119, true);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 15, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: karan
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 30, true);


--
-- PostgreSQL database dump complete
--

