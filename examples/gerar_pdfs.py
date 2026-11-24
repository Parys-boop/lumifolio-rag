"""Recria os PDFs didáticos. Requer ReportLab apenas para editar os exemplos."""

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

OUT = Path(__file__).resolve().parent
INK = HexColor("#162B29")
MUTED = HexColor("#435952")
PINE = HexColor("#246052")
PAPER = HexColor("#F6F8F3")
LINE = HexColor("#C8D6CC")

NOTES = {
    "pln-e-embeddings.pdf": (
        "Caderno de PLN",
        [
            (
                "Embeddings de texto",
                "Da linguagem natural aos vetores",
                [
                    ("Representação", "Um embedding resume propriedades de um texto em um vetor numérico. "
                     "O mesmo modelo representa a pergunta e os trechos em um espaço comum. "
                     "Um modelo multilíngue permite comparar frases em idiomas diferentes, embora o resultado também dependa do acervo e da tarefa."),
                    ("Vocabulário", "A busca por palavras exatas pode perder relações de sentido. "
                     "Por exemplo, “como reparar um veículo?” pode recuperar um texto sobre manutenção de automóveis, "
                     "mesmo sem repetir a palavra veículo. A ideia é comparar o sentido aproximado, sem exigir a mesma grafia."),
                    ("Limites", "Vetores parecidos indicam afinidade segundo o modelo. Uma dúvida sobre como consertar um automóvel "
                     "e um manual de como vender um automóvel ainda podem parecer próximos. "
                     "Por isso, a recuperação oferece candidatos que precisam ser lidos no contexto da pergunta."),
                ],
                "No índice, os vetores apontam para os trechos de origem, que podem ser abertos para conferência.",
            ),
            (
                "Similaridade de cosseno",
                "Como interpretar o ranking da busca",
                [
                    ("Comparação", "A similaridade de cosseno compara a direção dos vetores pelo ângulo entre eles. "
                     "Ela não depende do comprimento de cada vetor. Depois da normalização, o produto escalar de dois vetores também calcula "
                     "o cosseno entre eles."),
                    ("Ranking", "O índice ordena os trechos candidatos por proximidade com a consulta. "
                     "Trechos próximos costumam compartilhar assunto, mas a posição na lista não comprova a existência da resposta. "
                     "Uma escala de similaridade mede afinidade vetorial e não pode ser interpretada como probabilidade de acerto."),
                    ("Leitura crítica", "A pontuação muda quando usamos outro modelo de embeddings ou alteramos o acervo. "
                     "Para escolher um limiar, é preciso testar perguntas respondíveis e não respondíveis sob condições comparáveis, "
                     "registrando o modelo, o corpus e a configuração de busca."),
                ],
                "Compare consultas de significados parecidos que usem palavras diferentes.",
            ),
        ],
    ),
    "pratica-de-rag.pdf": (
        "Prática de RAG",
        [
            (
                "Divisão em trechos",
                "Preparação da base para a busca semântica",
                [
                    ("Chunking", "Em um sistema RAG, a fragmentação divide o material em unidades menores que podem ser indexadas e recuperadas. "
                     "No exercício, cada trecho preserva o número da página do PDF de origem, "
                     "de modo que o estudante consiga localizar a passagem no documento."),
                    ("Sobreposição", "O exercício mantém algumas palavras em comum entre trechos consecutivos para preservar o contexto "
                     "na fronteira entre eles. Se uma definição começar no fim de um trecho, a sobreposição reduz a chance "
                     "de perder sua continuação no próximo."),
                    ("Compromisso", "A sobreposição aumenta a redundância do índice e pode devolver duas janelas que compartilham grande parte do texto. "
                     "O tamanho dos trechos também deve limitar quanto texto entra no prompt. "
                     "Na apresentação, compare os trechos exibidos e observe se há repetição."),
                ],
                "Um trecho é uma janela do texto original vinculada a uma fonte que pode ser conferida.",
            ),
            (
                "Resposta fundamentada",
                "Da recuperação à confirmação da fonte",
                [
                    ("Contexto", "A etapa de recuperação seleciona passagens candidatas antes da geração. "
                     "O sistema pode atribuir um identificador temporário a cada passagem e inserir a lista no prompt, junto com a pergunta. "
                     "O modelo recebe instruções para fundamentar sua explicação nessas passagens."),
                    ("Conferência", "Para conferir uma citação, abra o trecho indicado e compare a afirmação com a passagem original. "
                     "Use o nome do arquivo e o número de página, se houver, para localizar a evidência. "
                     "É possível apresentar uma fonte existente que trata do mesmo assunto sem sustentar a conclusão."),
                    ("Limites", "Uma resposta deve indicar insuficiência de evidência se a passagem não contiver os dados necessários. "
                     "Esse cuidado também se aplica quando a pergunta parece relevante para o documento ou quando a pontuação da busca "
                     "é muito parecida com a de outras consultas."),
                ],
                "Encontrar o trecho e verificar se ele sustenta a afirmação são duas etapas da leitura.",
            ),
        ],
    ),
}


def paragraph(pdf, text, x, top, width, *, size, leading, color, font="Helvetica"):
    style = ParagraphStyle(
        "paragraph", fontName=font, fontSize=size, leading=leading, textColor=color, alignment=TA_LEFT
    )
    block = Paragraph(escape(text), style)
    _, height = block.wrap(width, top)
    block.drawOn(pdf, x, top - height)
    return top - height


def make_pdf(filename, series, pages):
    pdf = canvas.Canvas(str(OUT / filename), pagesize=A4, invariant=1, pageCompression=1)
    pdf.setTitle(series)
    pdf.setAuthor("Lumifólio")
    width, height = A4
    for number, (title, subtitle, sections, note) in enumerate(pages, start=1):
        pdf.setFillColor(white)
        pdf.rect(0, 0, width, height, fill=1, stroke=0)
        pdf.setFillColor(PINE)
        pdf.rect(0, height - 9, width, 9, fill=1, stroke=0)
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(54, height - 57, series.upper())
        pdf.setFillColor(INK)
        pdf.setFont("Helvetica-Bold", 32)
        pdf.drawString(54, height - 114, title)
        pdf.setFillColor(MUTED)
        pdf.setFont("Helvetica", 14)
        pdf.drawString(54, height - 142, subtitle)
        pdf.setStrokeColor(LINE)
        pdf.line(54, height - 168, width - 54, height - 168)

        y = height - 199
        for heading, body in sections:
            y = paragraph(pdf, heading, 54, y, width - 108, size=14, leading=18, color=PINE,
                          font="Helvetica-Bold")
            y = paragraph(pdf, body, 54, y - 10, width - 108, size=12, leading=18, color=INK) - 27

        if y < 155:
            raise RuntimeError(f"Texto excedeu a área da página {number} de {filename}")
        pdf.setFillColor(PAPER)
        pdf.roundRect(54, y - 61, width - 108, 61, 8, fill=1, stroke=0)
        paragraph(pdf, note, 69, y - 14, width - 138, size=12, leading=16, color=PINE)

        pdf.setStrokeColor(LINE)
        pdf.line(54, 60, width - 54, 60)
        pdf.setFont("Helvetica", 10)
        pdf.setFillColor(MUTED)
        pdf.drawString(54, 39, "Lumifólio / Material didático de demonstração")
        pdf.drawRightString(width - 54, 39, f"{number} / {len(pages)}")
        pdf.showPage()
    pdf.save()


if __name__ == "__main__":
    for name, (series_name, content) in NOTES.items():
        make_pdf(name, series_name, content)
