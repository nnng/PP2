import json
from datetime import date
from pathlib import Path

from psycopg2.extras import RealDictCursor

from db.connection import get_connection


DEFAULT_GROUP = 'Other'
VALID_PHONE_TYPES = {'home', 'work', 'mobile'}
VALID_SORTS = {
    'name': 'c.name ASC, c.surname ASC, c.id ASC',
    'birthday': 'c.birthday ASC NULLS LAST, c.name ASC, c.surname ASC, c.id ASC',
    'date added': 'c.created_at DESC, c.id DESC',
    'created_at': 'c.created_at DESC, c.id DESC',
}


def _normalize_text(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_phone_type(value):
    phone_type = _normalize_text(value)
    if not phone_type:
        return 'mobile'
    phone_type = phone_type.lower()
    return phone_type if phone_type in VALID_PHONE_TYPES else 'mobile'


def _normalize_birthday(value):
    value = _normalize_text(value)
    if not value:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def _normalize_contact_row(row):
    row = dict(row)
    phones_json = row.pop('phones_json', '[]')
    if isinstance(phones_json, str):
        phones = json.loads(phones_json)
    else:
        phones = phones_json or []

    birthday = row.get('birthday')
    if birthday is not None and hasattr(birthday, 'isoformat'):
        row['birthday'] = birthday.isoformat()

    created_at = row.get('created_at')
    if created_at is not None and hasattr(created_at, 'isoformat'):
        row['created_at'] = created_at.isoformat(sep=' ', timespec='seconds')

    row['group'] = row.pop('group_name', None) or DEFAULT_GROUP
    row['phones'] = phones
    row['full_name'] = f"{row.get('name', '')} {row.get('surname', '')}".strip()
    return row


def _build_contact_filters(query=None, group_name=None):
    conditions = []
    params = []

    if group_name:
        conditions.append('COALESCE(g.name, %s) ILIKE %s')
        params.extend([DEFAULT_GROUP, f"%{group_name.strip()}%"])

    if query:
        pattern = f"%{query.strip()}%"
        conditions.append(
            '('
            'c.name ILIKE %s OR '
            'c.surname ILIKE %s OR '
            "COALESCE(c.email, '') ILIKE %s OR "
            'EXISTS (SELECT 1 FROM phones px WHERE px.contact_id = c.id AND px.phone ILIKE %s) OR '
            'COALESCE(g.name, %s) ILIKE %s'
            ')'
        )
        params.extend([pattern, pattern, pattern, pattern, DEFAULT_GROUP, pattern])

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ''
    return where_clause, params


def _fetch_contacts(query=None, group_name=None, sort_by='name', limit=None, offset=None):
    sort_sql = VALID_SORTS.get((sort_by or 'name').strip().lower(), VALID_SORTS['name'])
    where_clause, params = _build_contact_filters(query=query, group_name=group_name)

    limit_clause = ''
    if limit is not None:
        limit_clause += ' LIMIT %s'
        params.append(int(limit))
    if offset is not None:
        limit_clause += ' OFFSET %s'
        params.append(int(offset))

    sql = f'''
        SELECT
            c.id,
            c.name,
            c.surname,
            c.email,
            c.birthday,
            c.created_at,
            COALESCE(g.name, %s) AS group_name,
            COALESCE(
                json_agg(json_build_object('phone', p.phone, 'type', p.type) ORDER BY p.id)
                    FILTER (WHERE p.id IS NOT NULL),
                '[]'::json
            )::text AS phones_json
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones p ON p.contact_id = c.id
        {where_clause}
        GROUP BY c.id, g.name
        ORDER BY {sort_sql}
        {limit_clause}
    '''

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(sql, [DEFAULT_GROUP, *params])
        return [_normalize_contact_row(row) for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


def _count_contacts(query=None, group_name=None):
    where_clause, params = _build_contact_filters(query=query, group_name=group_name)
    sql = f'''
        SELECT COUNT(*)
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        {where_clause}
    '''

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(sql, params)
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()


def normalize_contact_payload(contact):
    phones = contact.get('phones') or []
    normalized_phones = []

    for phone in phones:
        if isinstance(phone, dict):
            phone_value = _normalize_text(phone.get('phone'))
            phone_type = _normalize_phone_type(phone.get('type'))
        else:
            phone_value = _normalize_text(phone)
            phone_type = 'mobile'

        if phone_value:
            normalized_phones.append({'phone': phone_value, 'type': phone_type})

    primary_phone = _normalize_text(contact.get('phone'))
    if primary_phone and not normalized_phones:
        normalized_phones.append({
            'phone': primary_phone,
            'type': _normalize_phone_type(contact.get('phone_type')),
        })

    return {
        'name': _normalize_text(contact.get('name')),
        'surname': _normalize_text(contact.get('surname')),
        'email': _normalize_text(contact.get('email')),
        'birthday': _normalize_text(contact.get('birthday')),
        'group_name': _normalize_text(contact.get('group_name') or contact.get('group')),
        'phones': normalized_phones,
    }


def _find_contact_id(cursor, name, surname):
    cursor.execute(
        'SELECT id FROM contacts WHERE name = %s AND surname = %s',
        (name, surname)
    )
    row = cursor.fetchone()
    return row[0] if row else None


def _ensure_group_id(cursor, group_name):
    group_name = _normalize_text(group_name) or DEFAULT_GROUP
    cursor.execute(
        'INSERT INTO groups(name) VALUES (%s) ON CONFLICT (name) DO NOTHING',
        (group_name,)
    )
    cursor.execute('SELECT id FROM groups WHERE name = %s', (group_name,))
    return cursor.fetchone()[0]


def _fetch_contact_details(name, surname):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            '''
            SELECT
                c.id,
                c.name,
                c.surname,
                c.email,
                c.birthday,
                c.created_at,
                COALESCE(g.name, %s) AS group_name,
                COALESCE(
                    json_agg(json_build_object('phone', p.phone, 'type', p.type) ORDER BY p.id)
                        FILTER (WHERE p.id IS NOT NULL),
                    '[]'::json
                )::text AS phones_json
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            LEFT JOIN phones p ON p.contact_id = c.id
            WHERE c.name = %s AND c.surname = %s
            GROUP BY c.id, g.name
            ''',
            (DEFAULT_GROUP, _normalize_text(name), _normalize_text(surname))
        )
        row = cursor.fetchone()
        return _normalize_contact_row(row) if row else None
    finally:
        cursor.close()
        conn.close()


def upsert_contact(name, surname, phone=None, phone_type='mobile', email=None, birthday=None, group_name=None):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'CALL upsert_contact(%s, %s, %s, %s, %s, %s, %s)',
            (
                _normalize_text(name),
                _normalize_text(surname),
                _normalize_text(phone),
                _normalize_phone_type(phone_type),
                _normalize_text(email),
                _normalize_birthday(birthday),
                _normalize_text(group_name),
            )
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def save_contact_record(contact):
    contact = normalize_contact_payload(contact)
    phones = contact['phones']

    primary_phone = phones[0]['phone'] if phones else None
    primary_type = phones[0]['type'] if phones else 'mobile'

    upsert_contact(
        contact['name'],
        contact['surname'],
        primary_phone,
        primary_type,
        contact['email'],
        contact['birthday'],
        contact['group_name'],
    )

    full_name = f"{contact['name']} {contact['surname']}".strip()
    for phone in phones[1:]:
        add_phone_to_contact(full_name, phone['phone'], phone['type'])


def replace_contact(contact):
    contact = normalize_contact_payload(contact)
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'DELETE FROM contacts WHERE name = %s AND surname = %s',
            (contact['name'], contact['surname'])
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

    save_contact_record(contact)


def add_phone_to_contact(contact_name, phone, phone_type='mobile'):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'CALL add_phone(%s, %s, %s)',
            (_normalize_text(contact_name), _normalize_text(phone), _normalize_phone_type(phone_type))
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def move_contact_to_group(contact_name, group_name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'CALL move_to_group(%s, %s)',
            (_normalize_text(contact_name), _normalize_text(group_name))
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def delete_contact(value):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('CALL delete_contact_by_value(%s)', (_normalize_text(value),))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def search_contacts(query):
    query = _normalize_text(query)
    if not query:
        return get_contacts()

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute('SELECT * FROM search_contacts(%s)', (query,))
        return [_normalize_contact_row(row) for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


def get_contacts(query=None, group_name=None, sort_by='name', limit=None, offset=None):
    return _fetch_contacts(query=query, group_name=group_name, sort_by=sort_by, limit=limit, offset=offset)


def count_contacts(query=None, group_name=None):
    return _count_contacts(query=query, group_name=group_name)


def get_users(filter_value=None):
    return search_contacts(filter_value) if filter_value else get_contacts()


def get_users_paginated(limit, offset):
    return get_contacts(limit=limit, offset=offset)


def update_user(old_name, old_surname, new_name=None, new_surname=None, new_phone=None, new_phone_type=None, new_email=None, new_birthday=None, new_group=None):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        contact_id = _find_contact_id(cursor, _normalize_text(old_name), _normalize_text(old_surname))
        if contact_id is None:
            print('❌ Contact not found!')
            return

        if new_name:
            cursor.execute('UPDATE contacts SET name = %s WHERE id = %s', (_normalize_text(new_name), contact_id))

        if new_surname:
            cursor.execute('UPDATE contacts SET surname = %s WHERE id = %s', (_normalize_text(new_surname), contact_id))

        if new_email is not None:
            cursor.execute('UPDATE contacts SET email = %s WHERE id = %s', (_normalize_text(new_email), contact_id))

        if new_birthday is not None:
            cursor.execute('UPDATE contacts SET birthday = %s WHERE id = %s', (_normalize_birthday(new_birthday), contact_id))

        if new_group is not None:
            group_id = _ensure_group_id(cursor, new_group)
            cursor.execute('UPDATE contacts SET group_id = %s WHERE id = %s', (group_id, contact_id))

        if new_phone:
            cursor.execute(
                '''
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s, %s, %s)
                ON CONFLICT (contact_id, phone)
                DO UPDATE SET type = EXCLUDED.type
                ''',
                (contact_id, _normalize_text(new_phone), _normalize_phone_type(new_phone_type))
            )

        conn.commit()
        print('✅ Contact updated successfully!')
    except Exception as exc:
        conn.rollback()
        print(f'❌ Error: {exc}')
    finally:
        cursor.close()
        conn.close()


def delete_user(value):
    delete_contact(value)


def add_or_update_user(name, surname, phone):
    upsert_contact(name, surname, phone)


def insert_many_users(names, surnames, phones):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''
            CREATE TEMP TABLE IF NOT EXISTS invalid_users (
                name TEXT,
                surname TEXT,
                phone TEXT
            ) ON COMMIT DROP
            '''
        )
        cursor.execute('DELETE FROM invalid_users')

        if not (len(names) == len(surnames) == len(phones)):
            raise ValueError('Names, surnames, and phones arrays must have the same length')

        for name, surname, phone in zip(names, surnames, phones):
            phone_value = _normalize_text(phone)
            if phone_value and len(phone_value) >= 3:
                cursor.execute(
                    'CALL upsert_contact(%s, %s, %s, %s, %s, %s, %s)',
                    (
                        _normalize_text(name),
                        _normalize_text(surname),
                        phone_value,
                        'mobile',
                        None,
                        None,
                        None,
                    )
                )
            else:
                cursor.execute(
                    'INSERT INTO invalid_users(name, surname, phone) VALUES (%s, %s, %s)',
                    (_normalize_text(name), _normalize_text(surname), phone_value)
                )

        conn.commit()
    except Exception as exc:
        conn.rollback()
        print(f'❌ Error: {exc}')
    finally:
        cursor.close()
        conn.close()


def read_contacts_from_json(path):
    json_path = Path(path)
    with json_path.open('r', encoding='utf-8') as file:
        payload = json.load(file)

    if isinstance(payload, dict) and 'contacts' in payload:
        payload = payload['contacts']

    if not isinstance(payload, list):
        raise ValueError('JSON must contain a list of contacts or an object with a contacts key')

    return payload


def export_contacts_to_json(path):
    contacts = get_contacts(sort_by='name')
    json_path = Path(path)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    with json_path.open('w', encoding='utf-8') as file:
        json.dump(contacts, file, ensure_ascii=False, indent=2)


def get_contact_details(name, surname):
    return _fetch_contact_details(name, surname)


def upsert_user(name, surname, phone):
    return upsert_contact(name, surname, phone)


def search_phonebook(query):
    return search_contacts(query)


def delete_user_by_value(value):
    return delete_contact(value)


def get_phonebook_paginated(limit, offset):
    return get_users_paginated(limit, offset)