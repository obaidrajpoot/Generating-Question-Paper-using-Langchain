import re
def preprocess(text):
    remove_title = ['references','index','bibliography','works cited']
    clean_doc = []
    for texting in text:
        texting = re.sub(r'\[.*?\]\(.?\)|https?://\S+|www\.\S+', '', texting)
        texting = re.sub(r'[\u200b\u200c\u200d\ufeff]+', '', texting)
        texting = re.sub(r'[‣•▪▫●◦‒–—―→⇒]+', '', texting)
        texting = re.sub(r'\s+', ' ', texting) 
        texting = texting.lower().strip() 
        if not texting:
            continue
        if any(t in texting for t in remove_title):
            continue
        clean_doc.append(texting)
    return clean_doc