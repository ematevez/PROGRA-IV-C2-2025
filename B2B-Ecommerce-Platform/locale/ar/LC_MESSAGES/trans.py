from googletrans import Translator
from django.conf import settings

translator = Translator()

untranslated = list()

with open("./django.po", "r") as file:
    line_number = 0
    for line in file.readlines():
        line_number += 1
        if 'msgid ""' in line:
            msgid_line = line
        if 'msgstr ""' in line and msgid_line != 'msgid ""\n':
            untranslated.append({"line_number": line_number, "msgid": msgid_line})

    # with open('./django', 'w') as write_file:
    #   write_line_number = 0;
    #  for write_line in file.readlines():
    #     write_line_number += 1
    #    write_file.writelines()


print(untranslated)
