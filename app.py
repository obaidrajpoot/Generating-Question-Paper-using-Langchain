from fastapi import Request, FastAPI, UploadFile, File, Form,HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,StreamingResponse
import io,os
from fpdf import FPDF
from generate_questions import generate_question
app = FastAPI()

template = Jinja2Templates(directory='templates')

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("DejaVu", "", "C:/Users/obaid/Desktop/questions_chatbot/dejavu-fonts-ttf-2.37/ttf/DejaVuSans.ttf", uni=True)
    

    def section_title(self, title):
        self.set_font("DejaVu", "B", 14)
    
        self.cell(0, 10, str(title), ln=True,align="C")
        self.ln(2)

    def question(self, text):
        self.set_font("DejaVu", "", 11)
        self.multi_cell(0, 7, txt=str(text))
        self.ln(1)


    def option(self, text):
        self.set_font("DejaVu", "", 11)
        self.set_x(20)
        self.multi_cell(0, 7, txt=str(text))


# Home page
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return template.TemplateResponse("paper_frontend.html", {"request": request})

@app.post("/generate_questions")
async def generate_questions(
    file: UploadFile = File(...),
    mcq: str = Form(...),
    fill: int = Form(...),
    shortq: int = Form(...),
    longq: int = Form(...),
    difficulty: str = Form(...)):

    file_folder ="C:/Users/obaid/Desktop/questions_chatbot/pdf_files"
    os.makedirs(file_folder,exist_ok=True)
    for filename in os.listdir(file_folder):
        if filename.lower().endswith(".pdf"):
            file_path=os.path.join(file_folder,filename)
            os.remove(file_path)
            print("old file is deleted:--")
    file_content =await file.read()
    filepath=f"C:/Users/obaid/Desktop/questions_chatbot/pdf_files/{file.filename}"
    with open(filepath,"wb") as f:
        f.write(file_content)
    print(difficulty,shortq,longq,mcq,fill)
    questions_generated=generate_question(difficulty,shortq,longq,mcq,fill)
    
    questions_generated=questions_generated.replace("**","").strip()
    print(questions_generated)

    return {
        "message": "Data is received",
        "question_generated":questions_generated
    }
@app.post("/pdf_download")
async def pdf_download(request: Request):
    try:
        data = await request.json()
        text = str(data.get("content", ""))
       
        pdf = PDF()  # <-- USE CUSTOM CLASS
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        for line in text.split("\n"):
            clean = str(line.strip())
            print("DEBUG CLEAN:",type(clean)) 

            if clean.startswith("**SECTION"):
                pdf.section_title(clean.replace("**", ""))
            elif clean.startswith(("A.", "B.", "C.", "D.")):
                pdf.option(clean)
            elif clean.startswith("Q"):
                pdf.question(clean)
            else:
                pdf.set_font("DejaVu",size= 12)
                pdf.multi_cell(0, 8, clean)
                pdf.ln(1)

        # Convert to PDF bytes
                
        pdf_bytes = pdf.output(dest="S")



        pdf_buffer = io.BytesIO(pdf_bytes)
        pdf_buffer.seek(0)

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=generated.pdf"}
        )
    except Exception as e:
        print("PDF DOWNLOAD ERROR:", repr(e))
        raise HTTPException(status_code=400, detail=f"error processing request: {str(e)}")


@app.post("/text_download")
async def text_download(request:Request):
    data=await request.json()
    text=data.get("content","")
    txt_buffer =io.BytesIO()
    txt_buffer.write(text.encode("utf-8"))
    txt_buffer.seek(0)
    return StreamingResponse(txt_buffer,media_type="text/plain",headers={'Content-Disposition':"attachment;filename=generated.txt"})