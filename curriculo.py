import streamlit as st
from fpdf import FPDF
from google import genai

# --- 1. CONFIGURAÇÃO VISUAL DO PDF (MAIS ELEGANTE) ---
class PDF_CV(FPDF):
    def header(self):
        # Nome no topo, bem destacado
        pass # Deixamos o cabeçalho para ser feito direto na função para ter mais controle
    
    def section_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0) # Preto
        self.cell(0, 8, title, ln=True)
        # Desenha uma linha fina e elegante abaixo do título
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(3) # Espaço depois da linha

def gerar_curriculo_ats(dados):
    pdf = PDF_CV()
    pdf.add_page()
    
    # --- Cabeçalho ---
    pdf.set_font('Arial', 'B', 22)
    pdf.cell(0, 10, dados['nome'].upper(), ln=True, align='L')
    
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(80, 80, 80) # Cinza escuro para os dados de contato
    info_contato = f"{dados['idade']} anos | {dados['cidade']} | {dados['email']} | {dados['telefone']}"
    pdf.cell(0, 6, info_contato, ln=True)
    pdf.ln(8)
    pdf.set_text_color(0, 0, 0) # Volta para preto

    # --- Formação Acadêmica ---
    if dados['educacao'][0]['instituicao'] != "":
        pdf.section_title("FORMAÇÃO ACADÊMICA")
        for edu in dados['educacao']:
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 6, edu['instituicao'], ln=True)
            pdf.set_font('Arial', '', 11)
            pdf.cell(0, 6, f"{edu['curso']} - {edu['periodo']}", ln=True)
        pdf.ln(5)

    # --- Experiência Profissional ---
    if dados['experiencia_formatada'] != "":
        pdf.section_title("EXPERIÊNCIA PROFISSIONAL")
        pdf.set_font('Arial', '', 11)
        
        # Limpeza pesada: substituindo caracteres especiais da IA por versões simples do teclado
        texto_seguro = dados['experiencia_formatada']
        texto_seguro = texto_seguro.replace('•', '-') # Bolinha
        texto_seguro = texto_seguro.replace('–', '-') # Traço médio (En-dash)
        texto_seguro = texto_seguro.replace('—', '-') # Traço longo (Em-dash)
        texto_seguro = texto_seguro.replace('“', '"').replace('”', '"') # Aspas duplas curvas
        texto_seguro = texto_seguro.replace('‘', "'").replace('’', "'") # Aspas simples curvas
        
        pdf.multi_cell(0, 6, texto_seguro)
        pdf.ln(5)

    # --- Cursos e Certificações ---
    cursos_validos = [c for c in dados['cursos'] if c.strip() != ""]
    if len(cursos_validos) > 0:
        pdf.section_title("CURSOS E CERTIFICAÇÕES")
        pdf.set_font('Arial', '', 11)
        for curso in cursos_validos:
            pdf.cell(0, 6, f"- {curso}", ln=True)

    nome_arquivo = f"CV_{dados['nome'].replace(' ', '_')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo


# --- 2. O CÉREBRO DA IA (O PROMPT) ---
def melhorar_texto_com_ia(texto_bruto, api_key):
    # O .strip() remove espaços invisíveis antes e depois da chave
    chave_limpa = api_key.strip() 
    
    # Nova forma de conectar com a biblioteca google-genai
    client = genai.Client(api_key=chave_limpa)
    
    # AQUI ESTÃO AS INSTRUÇÕES PARA A IA!
    prompt = f"""
    Você é um recrutador sênior otimizando o currículo de um candidato.
    O candidato descreveu suas experiências de forma bagunçada abaixo. 
    
    Sua tarefa:
    1. Organize o texto separando as experiências.
    2. Para cada experiência, crie um cabeçalho no formato: "Cargo (Período) - Nome da Empresa" (se a empresa não for citada, omita).
    3. Abaixo do cabeçalho, reescreva as atividades que a pessoa fazia em formato de tópicos.
    4. Use verbos de ação profissionais (ex: Gerenciei, Atendi, Realizei, Operei).
    5. REGRA DE OURO: Nunca use a bolinha (•) para os tópicos, use SEMPRE o símbolo de hífen (-).
    6. Não inclua textos como "Aqui está sua experiência formatada", me devolva apenas o conteúdo pronto para o currículo.
    
    Texto do candidato:
    {texto_bruto}
    """
    
    # Chamando o modelo correto (gemini-flash-latest) com a nova sintaxe
    resposta = client.models.generate_content(
        model='gemini-flash-latest',
        contents=prompt
    )
    return resposta.text


# --- 3. INTERFACE STREAMLIT ---
st.set_page_config(page_title="Gerador de Currículo Inteligente", layout="wide")

# Barra lateral para colocar a chave da IA
with st.sidebar:
    st.header("⚙️ Configuração da Inteligência Artificial")
    st.write("Para a IA analisar as experiências, cole sua chave do Google Gemini abaixo:")
    chave_api = st.text_input("Chave API (Gemini)", type="password")
    st.info("Sem a chave, o app vai gerar o currículo com o texto exatamente como você digitar.")

st.title("🚀 Gerador de Currículo")
st.write("Preencha os dados e deixe a Inteligência Artificial organizar sua experiência.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 Dados Pessoais")
    nome = st.text_input("Nome Completo", placeholder="Ex: Nome Sobrenome")
    contato = st.text_input("E-mail", placeholder="Ex: fulano@gmail.com")
    fone = st.text_input("Telefone", placeholder="(11) 99999-9999")
    cidade = st.text_input("Cidade/UF", placeholder="São Paulo - SP")
    idade = st.number_input("Idade", min_value=14, max_value=100, value=21)

with col2:
    st.subheader("🎓 Formação e Cursos")
    faculdade = st.text_input("Universidade/Escola", placeholder="Ex: Universidade Anhembi Morumbi")
    curso_grad = st.text_input("Curso", placeholder="Ex: Administração")
    status_curso = st.selectbox("Status", ["Concluído", "Em andamento", "Trancado"])
    certificacoes = st.text_area("Cursos Extras (um por linha)", placeholder="Ex: Excel Básico - Senai\nInglês Básico - Fisk")

st.subheader("💼 Experiência Profissional")
exp_texto = st.text_area(
    "Escreva como se estivesse conversando. Ex: 'Trabalhei de atendente de janeiro a agosto de 2024 na loja X, eu fechava caixa e ajudava clientes no zap'. A IA vai transformar isso em algo profissional!",
    height=150
)

if st.button("✨ Gerar Currículo Otimizado", use_container_width=True):
    if not nome:
        st.error("Por favor, preencha pelo menos o Nome Completo.")
    else:
        with st.spinner("Processando..."):
            # Lógica da IA
            texto_experiencia_final = exp_texto
            
            # Só chama a IA se tiver texto de experiência E se a pessoa colocou a chave da API
            if exp_texto.strip() != "" and chave_api != "":
                try:
                    texto_experiencia_final = melhorar_texto_com_ia(exp_texto, chave_api)
                except Exception as e:
                    st.error(f"Erro ao conectar com a IA. Gerando com o texto original... (Erro: {e})")

            # Estrutura de dados limpa (sem os dados falsos de antes)
            dados_usuario = {
                "nome": nome, "email": contato, "telefone": fone, "cidade": cidade, "idade": idade,
                "educacao": [{"instituicao": faculdade, "curso": curso_grad, "periodo": status_curso}],
                "experiencia_formatada": texto_experiencia_final, # Passamos o texto que a IA fez
                "cursos": certificacoes.split('\n')
            }
            
            # Gera o PDF
            arquivo = gerar_curriculo_ats(dados_usuario)
            
            st.success("Currículo pronto!")
            with open(arquivo, "rb") as f:
                st.download_button("📥 Baixar Currículo em PDF", data=f, file_name=arquivo, mime="application/pdf")
            
            # Mostra como a IA deixou o texto para o usuário ver na tela
            if chave_api != "" and exp_texto.strip() != "":
                st.info("Veja como a IA transformou seu texto:")
                st.text(texto_experiencia_final)