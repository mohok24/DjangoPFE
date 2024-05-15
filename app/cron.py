from django_cron import CronJobBase, Schedule
import glob
import datetime
import re
import shutil
import spacy
from docx import Document
from models import DocumentFolderPath
from models import Report,Patient
class MyCronJob(CronJobBase):
    RUN_AT_TIMES = ['00:00'] 

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'app.classify' 
    
    def do(self):
        def reinitialize():
                global left_side_sentences
                global right_side_sentences
                global both_sides_sentences
                global no_side_sentences 
                left_side_sentences=[]
                right_side_sentences=[]
                both_sides_sentences=[]
                no_side_sentences=[]
        def frenchtoiso(date_str):
            french_month_names = {
                'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
                'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
            }
            day_name, day, month_name, year = date_str.split()
            month = french_month_names[month_name.lower()]
            date_obj = datetime.datetime.strptime(f"{day} {month} {year}", "%d %m %Y")
            iso_date_str = date_obj.strftime("%Y-%m-%d")
            return iso_date_str
        left_keywords = ["gauche", "left"]
        right_keywords = ["droite", "right","droit"]
        both_keywords = ["trame conjonctivo glandulaire","aire axillaire libre","système canalaire non dilaté","axillaires libres","ganglions axillaires bilatéraux","au niveau des deux seins","bilatéraux","plans graisseux sous cutanés","revêtement cutané fin et régulier", "foyers","homogènes","seins à trame","bilatéral", "bilateral","absence ","cutané fin régulier","acr", "bilatérale"]
        nlp = spacy.load("fr_core_news_md")
        left_side_sentences = []
        right_side_sentences = []
        both_sides_sentences = []
        no_side_sentences= []
        def move_file(source_path, destination_folder):
            shutil.move(source_path, destination_folder)
        destination_folder = "D:/reports/processed"

        def split_paragraph(paragraph):
            sentences = []
            current_sentence = ""
            for sentence in paragraph.split('\n'):
                sentence.strip()
                if sentence.endswith(':') or sentence.endswith(': ') or sentence.endswith('.'):
                    sentences.append(sentence)
                else:
                    current_sentence += sentence.strip()

            return sentences
        def left_right(sentence):
            global left_keywords
            global right_keywords
            global both_keywords
            global left_side_sentences
            global right_side_sentences
            global both_sides_sentences
            global no_side_sentences
            if any(keyword in sentence.lower() for keyword in both_keywords):
                                    both_sides_sentences.append(sentence)
            elif any(keyword in sentence.lower() for keyword in left_keywords) and any(keyword in sentence.lower() for keyword in right_keywords):
                                    both_sides_sentences.append(sentence)
            elif any(keyword in sentence.lower() for keyword in right_keywords):
                                    right_side_sentences.append(sentence)
            elif any(keyword in sentence.lower() for keyword in left_keywords):
                                    left_side_sentences.append(sentence)
            else:
                                       no_side_sentences.append(sentence)   
        def left_rightadd(sentence1,sentence):
            global left_keywords
            global right_keywords 
            global both_keywords 
            global left_side_sentences
            global right_side_sentences
            global both_sides_sentences
            global no_side_sentences
            if any(keyword in sentence.lower() for keyword in both_keywords):
                                    both_sides_sentences.append((sentence1,sentence))
            elif any(keyword in sentence.lower() for keyword in right_keywords):
                                        right_side_sentences.append((sentence1,sentence))
            elif any(keyword in sentence.lower() for keyword in left_keywords):
                                     left_side_sentences.append((sentence1,sentence))
            else:
                                       no_side_sentences.append((sentence1,sentence))
        def classify_sentences(text,type):
            test=split_paragraph(text)
            priority_found = False
            reference_sentence = "QSE gauche de 4mm"
            reference_sentence2= "QIE droit : 7,8mm"
            reference_sentence4="QME gauche : 10 mm et micro-kyste remanié de 04,5 mm"
            prio_keywords=["pour cible","comme suit","et mesurant :","et mesurant:","pour cible :"]
            newtext = ''
            reference_tokens=nlp(reference_sentence)
            reference2_tokens=nlp(reference_sentence2)
            reference4_tokens=nlp(reference_sentence4)

            for sentence in test:
                newtext=sentence.replace('-',' ')
                newtext=newtext.strip()        
                if any(keyword in newtext.lower() for keyword in prio_keywords):
                                priority_found = True
                                priority_sentence=newtext
                                both_sides_sentences.append(newtext)
                elif priority_found == True and not newtext.isspace():
                                merged_tokens=nlp(newtext)
                                similarity=reference_tokens.similarity(merged_tokens)
                                similarity2=reference2_tokens.similarity(merged_tokens)
                                similarity4=reference4_tokens.similarity(merged_tokens)
                                if similarity >=0.5 or similarity2>=0.5 or similarity4>=0.5:
                                    left_rightadd(priority_sentence,newtext)
                                else:
                                    priority_found= False
                                    left_right(newtext)      
                else: left_right(newtext)       


            print("Sentences referring to the left side:")
            for sentencee in left_side_sentences:
                if(type=='m'):
                    nreport.leftM=nreport.leftM+sentencee
                else:
                    nreport.leftE=nreport.leftE+sentencee
                print("-", sentencee)

            print("\nSentences referring to the right side:")
            for sentencee in right_side_sentences:
                if(type=='m'):
                    nreport.rightM=nreport.rightM+sentencee
                else:
                    nreport.rightE=nreport.rightE+sentencee
                print("-", sentencee)

            print("\nSentences referring to both sides:")
            for sentencee in both_sides_sentences:
                if(type=='m'):
                    nreport.bothM=nreport.bothM+sentencee
                else:
                    nreport.bothE=nreport.bothE+sentencee
                print("-", sentencee)

            print("\nSentences not specifying a side:")
            for sentencee in no_side_sentences:
                if(type=='m'):
                    nreport.noneM=nreport.noneM+sentencee
                else:
                    nreport.noneE=nreport.noneE+sentencee
                print("-", sentencee)
        
        def extract_text_from_docx(docx_file_path):
            doc = Document(docx_file_path)

            text = []
            for paragraph in doc.paragraphs:
                text.append(paragraph.text.replace("\xa0"," "))
            return text


        keywords = [
            'dépistage',
            'prévoir',
            'est souhaitable',
            'nécessitant',
            'à compléter par',
            'recontrôler',
            'toutefois nous recommandons',
            'contrôle',
            'histologique',
    
        ]


        try:
            document_folder_path = DocumentFolderPath.objects.get(pk=1) 
            folder_path = document_folder_path.folder_path
        except DocumentFolderPath.DoesNotExist:
            folder_path = 'D:\\reports\\meow'
        files = glob.glob(folder_path + '\\*.docx')

        #docx_file_path = 'D:\\reports\\pat-997-EXAM-1334696.docx'
        #extracted_text = extract_text_from_docx(docx_file_path)
        #for paragraph in extracted_text:
        #    print(paragraph)
    
        conctype_pattern = re.compile(r'Mammographie\s*(bilaterale|unilaterale|unilatérale|bilatérale)\s*(gauche|droite)?\s*(et (échographie)|(echographie) mammaire)?',re.IGNORECASE)
        type_pattern = re.compile(r'(MAMMOGRAPHIE\s*(/\s*ECHO COMPRISE)|(\s*BILATERALE))',re.IGNORECASE)
        name_pattern = re.compile(r'(Nom, Prénom : (.+?) \d+ ANS)|(Patient(e) : (.+?) \d+ ANS)') 
        age_pattern = re.compile(r'(\d+) ANS',re.IGNORECASE)
        date_pattern = re.compile(r'\b(?:(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\s(\d{1,2})\s(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|decembre|fevrier|aout)\s(\d{4}))\b')
        indic_pattern = re.compile(r'(?:motif|indication|MOTIF|INDICATION)\s*:\s*(.+?)\.',re.IGNORECASE)
        mammography_pattern = re.compile(r'RESULTATS\s*:?\s*(?:\s*Mammographie\s*(?:bilatérale)?:*,*,*\s*)?(.*?)(?:\s*Le\s+complément\s+échographique\s*|\s*échographie\s+mammaire\s*:\s*|Echographie\s*mammaire|Echographie|Conclusion\s*:?|$)'
        ,re.IGNORECASE | re.DOTALL)
        acr_pattern = re.compile(r"type [abcd] de l’ACR", re.IGNORECASE)  
        echo_pattern = re.compile(r"(?:Le\s*complément\s*échographique\s*|\s*échographie\s+mammaire\s*|\s*echographie\s*mammaire\s*|\s*echographie\s*)(?:,|:)?(.*?)(?=\s*Conclusion|$|Examen)",re.IGNORECASE|re.DOTALL)
        recom_pattern = re.compile(r'[^.:,]*?(?:\b(?:' + '|'.join(re.escape(word) for word in keywords) + r')\b).*?(?=\.)', re.IGNORECASE|re.DOTALL)
        conclusion_pattern = re.compile(r'(?:conclusion)\s*(.+)(?:$|Identification)',re.IGNORECASE|re.DOTALL)
        left_pattern = re.compile(r'((Sein\s*sous\s*cicatriciel\s*gauche)(|Sein gauche\s*:))(.*?)(?:Sein\s*droit|conclusion)',re.IGNORECASE | re.DOTALL)
        right_pattern = re.compile(r'((Sein\s*sous\s*cicatriciel\s*droit)|(Sein\s*droit\s*:))(.*?)(?:Sein\s*gauche|$)',re.IGNORECASE | re.DOTALL)
        left_classification_pattern = re.compile(r"((et)?(sein\s*gauche\s*)?(((classant\s*l'examen)|(examen\s*(classée|classé|classee|class|classées))|(classée)|(classé))?\s*bi-rads\s*[0-6]\s*[a,b,c]?)\s*(de l('|’)ACR)?\s*([a,à]\s*gauche\s*)|(comme à gauche))|((et)?(sein\s*gauche\s*)(((classant\s*l'examen)|(examen\s*(classée|classé|classee|class|classées))|(classée)|(classé))?\s*bi-rads\s*[0-6]\s*[a,b,c]?)\s*(de l('|’)ACR)?\s*)|(Examen du sein gauche\s*(?:.*?)bi-rads\s*[0-6]\s*[a,b,c]?)", re.IGNORECASE|re.DOTALL)
        right_classification_pattern = re.compile(r"((et)?(sein\s*droit\s*)?(((classant\s*l'examen)|(examen\s*(classée|classé|classee|class|classées))|(classée)|(classé))?\s*bi-rads\s*[0-6]\s*[a,b,c]?(\s*versus [0-6]\s*[a,b,c]?)?)\s*(de l('|’)ACR)?\s*([a,à]\s*droite\s*)|(comme à droite))|((et)?(sein\s*droit\s*)(((classant\s*l'examen)|(examen\s*(classée|classé|classee|class|classées))|(classée)|(classé))?\s*bi-rads\s*[0-6]\s*[a,b,c]?)\s*(de l('|’)ACR)?\s*)|(Examen du sein droit\s*(?:.*?)bi-rads\s*[0-6]\s*[a,b,c]?)",re.IGNORECASE|re.DOTALL)
        both_classification_pattern = re.compile(r"(bi-rads\s*[0-6]\s*[a,b,c]?)\s*(de l('|’)ACR)?",re.IGNORECASE|re.DOTALL)


        for file in files:
            nreport=Report.objects.create()
            leftm = None;
            rightm = None;
            extracted_text = extract_text_from_docx(file)
            text = '\x0a'.join(extracted_text)
            name_match = name_pattern.search(text)
            age_match = age_pattern.search(text)
            indic_match = indic_pattern.search(text)
            mammo_match = mammography_pattern.search(text)
            acr_match = acr_pattern.search(text)
            echo_match = echo_pattern.search(text)
            recom_match = recom_pattern.search(text)
            conclusion_match = conclusion_pattern.search(text)
            date_match=date_pattern.search(text)
    

            patient_name = name_match.group(1) if name_match else None
            patient_age = int(age_match.group(1)) if age_match else None
            indication = indic_match.group(1) if indic_match else None
            mammo = mammo_match.group(1) if mammo_match else None
            acr = acr_match.group() if acr_match else None
            echo = echo_match.group(1) if echo_match else None
    
            left_match = left_pattern.search(echo)
            right_match = right_pattern.search(echo)
            leftm_match = left_pattern.search(mammo)
            rightm_match = right_pattern.search(mammo)
    
            recommendation = recom_match.group() if recom_match else None
            date=date_match.group() if date_match else None
            conclusion = conclusion_match.group(1) if conclusion_match else None
            left_class_match=left_classification_pattern.search(conclusion)
            left_classification=re.finditer(left_classification_pattern,conclusion)
            right_class_match=right_classification_pattern.search(conclusion)
            right_classification=re.finditer(right_classification_pattern,conclusion)
            both_class_match=both_classification_pattern.search(conclusion)
            both_classification=re.finditer(both_classification_pattern,conclusion) 
            conctype_match=conctype_pattern.search(conclusion) 
            type=conctype_match.group() if conctype_match else None
            if conctype_match: 
                nreport.type=conctype_match
            else:
                type=type_pattern.search(text) 
                type=type.group() if type else None
                nreport.type=type;
            
        
    
            if recommendation!=None:
                    recommendation=recommendation.strip()
            if indication!=None:
                    indication=indication.strip()
            matches=re.findall(recom_pattern,text)
            for x in matches:
                    b=x.strip()
                    if b==indication:
                        matches.remove(x)            
            if not (left_match or right_match): 
                classify_sentences(echo,'e')
                reinitialize()
                left = None
                right = None
            else:
                if(left_match):
                    left=left_match.group()
                    nreport.leftE=left
                if(right_match):
                    right=right_match.group()
                    nreport.rightE=right
            if not (leftm_match or rightm_match):
                classify_sentences(mammo,'m')   
                reinitialize()
                left = None
                right = None
            else:
                if(leftm_match):
                    leftm=leftm_match.group()
                    nreport.leftM=leftm
                if(rightm_match):
                    rightm=rightm_match.group()
                    nreport.rightM=rightm
        
            for x in matches:
                nreport.indication=nreport.indication+x
            date=frenchtoiso(date)
            nreport.date=date
            if left:
                print("left:",left)
                print("right:",right)
            if leftm:
                print("left mammo:",leftm)
                print("right mammo:",rightm)
            print("Mammo results:",mammo)
            print("TYPE:",type)    
            for match in left_classification:
                leftc_match=match.group()
                print(f"left Match found: '{match.group()}' at position {match.start()}-{match.end()}")
                nreport.leftclassification=match.group()
     
            for match in right_classification:
                rightc_match = match.group()
                print(f"right match found:'{match.group()}' at position {match.start()}-{match.end()}")
                nreport.rightclassification=match.group()

            if not (rightc_match or leftc_match):
                for match in both_classification:
                    both_match=match.group()
                    print(f"both Match found: '{match.group()}' at position {match.start()}-{match.end()}")
                    nreport.bothclassification=match.group()
    
            rightc_match=[]
            leftc_match=[]
            existing_patient=Patient.objects.filter(firstname=patient_name)
            nreport.save()
            move_file(file,destination_folder)
        pass