def get_description_snippet_text(ds):
    string = ""
    for t in ds:
        try:
            if t['bold']:
                text = "<b>"+t['text']+"</b>"
            else:
                text = t['text']
        except:
            text = t['text']
        string = string + text
    return string