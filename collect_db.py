from lxml import etree
import sqlite3
import re


def parser(filename) -> list:
    with open(filename, 'r', encoding='utf-8') as xml:
        xml_source = xml.read()
    root = etree.fromstring(
        bytes(xml_source, encoding='utf-8')
    )
    lines = [item.text for item in root.findall('*//p', namespaces=root.nsmap)]

    return lines


def write_to_db(lines: list):
    connection = sqlite3.connect('tasks.db')
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Tasks(
        id INTEGER PRIMARY KEY,
        number INTEGER,
        task TEXT NOT NULL,
        answer TEXT NOT NULL
        )
        """
    )
    connection.commit()

    for line in lines:
        if line[0].isdigit():
            # print(line)

            m = re.match(r"(\d+). (.*)\[(.*)\]", line)
            number = int(m.group(1))
            task = m.group(2)
            answer = m.group(3)

            # print(f"{number=}, {task=}, {answer=}")

            cursor.execute(
                """
                INSERT INTO Tasks (number, task, answer) VALUES (?, ?, ?)
                """,
                (number, task, answer)
            )

            connection.commit()
    connection.close()


if __name__ == '__main__':
    raw_data = parser('input.fb2')
    write_to_db(raw_data)
