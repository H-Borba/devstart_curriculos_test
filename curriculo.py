import streamlit as st
from fpdf import FPDF
from google import genai

# --- 1. CONFIGURAÇÃO DA CHAVE (USANDO SECRETS) ---
try:
    CHAVE_API_GEMINI = st.secrets["GEMINI_API_KEY"]
except:
    CHAVE_API_GEMINI = ""

# --- 2. CONFIGURAÇÃO VISUAL DO PDF ---
class PDF_CV(FPDF):
    def header(self):
        pass 
    
    def section_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, title, ln=True)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(3)

def gerar_curriculo_ats(dados):
    pdf = PDF_CV()
    pdf.add_page()
    
    # --- Cabeçalho ---
    pdf.set_font('Arial', 'B', 22)
    pdf.cell(0, 10, dados['nome'].upper(), ln=True, align='L')
    
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(80, 80, 80)
    
    contatos = [f"{dados['idade']} anos", dados['cidade'], dados['telefone'], dados['email']]
    if dados['linkedin']:
        contatos.append(dados['linkedin'])
        
    info_contato = " | ".join([c for c in contatos if c.strip()])
    pdf.cell(0, 6, info_contato, ln=True)
    pdf.ln(8)
    pdf.set_text_color(0, 0, 0)

    # =========================================================
    # CAMINHO 1: USUÁRIO SEM EXPERIÊNCIA (OBJETIVO + SKILLS)
    # =========================================================
    if not dados['tem_experiencia']:
        # Objetivo
        if dados['objetivo'].strip():
            pdf.section_title("OBJETIVO PROFISSIONAL")
            pdf.set_font('Arial', '', 11)
            # Limpeza rápida de aspas da IA
            obj_seguro = dados['objetivo'].replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
            pdf.multi_cell(0, 6, obj_seguro)
            pdf.ln(5)
            
        # Competências
        if dados['soft_skills'].strip():
            pdf.section_title("COMPETÊNCIAS E HABILIDADES")
            pdf.set_font('Arial', '', 11)
            habilidades = dados['soft_skills'].replace(',', '\n').split('\n')
            for hab in habilidades:
                if hab.strip():
                    pdf.cell(0, 6, f"- {hab.strip()}", ln=True)
            pdf.ln(5)

    # --- Formação Acadêmica/Escolar (COMUM AOS DOIS) ---
    if dados['formacao_local'].strip():
        pdf.section_title("FORMAÇÃO ACADÊMICA")
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 6, dados['formacao_local'], ln=True)
        
        # Monta a linha do curso e adiciona a data caso o usuário tenha preenchido
        pdf.set_font('Arial', '', 11)
        linha_curso = f"{dados['formacao_curso']} - {dados['formacao_status']}"
        if dados['formacao_data'].strip():
            linha_curso += f" ({dados['formacao_data']})"
            
        pdf.cell(0, 6, linha_curso, ln=True)
        pdf.ln(5)

    # =========================================================
    # CAMINHO 2: USUÁRIO COM EXPERIÊNCIA
    # =========================================================
    if dados['tem_experiencia'] and dados['experiencia_formatada'].strip():
        pdf.section_title("EXPERIÊNCIA PROFISSIONAL")
        pdf.set_font('Arial', '', 11)
        
        texto_seguro = dados['experiencia_formatada']
        texto_seguro = texto_seguro.replace('•', '-').replace('–', '-').replace('—', '-')
        texto_seguro = texto_seguro.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
        
        pdf.multi_cell(0, 6, texto_seguro)
        pdf.ln(5)

    # --- Cursos e Certificações (COMUM AOS DOIS) ---
    cursos_validos = [c for c in dados['cursos'] if c.strip() != ""]
    if len(cursos_validos) > 0:
        pdf.section_title("CURSOS EXTRAS E CERTIFICAÇÕES")
        pdf.set_font('Arial', '', 11)
        for curso in cursos_validos:
            pdf.cell(0, 6, f"- {curso}", ln=True)

    nome_arquivo = f"CV_{dados['nome'].replace(' ', '_')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo


# --- 3. OS CÉREBROS DA IA ---

# Cérebro 1: Para quem tem experiência
def melhorar_experiencia_ia(texto_bruto):
    client = genai.Client(api_key=CHAVE_API_GEMINI.strip())
    prompt = f"""
    Você é um recrutador sênior otimizando o currículo de um candidato.
    O candidato descreveu suas experiências abaixo. 
    
    Sua tarefa:
    1. Organize o texto separando as experiências.
    2. Crie cabeçalhos no formato: "Cargo (Período) - Nome da Empresa".
    3. Abaixo, reescreva as atividades em formato de tópicos.
    4. Use verbos de ação profissionais.
    5. REGRA DE OURO: Nunca use a bolinha, use apenas hífen (-).
    6. Devolva APENAS o conteúdo pronto para o documento.
    
    Texto original: {texto_bruto}
    """
    resposta = client.models.generate_content(model='gemini-flash-latest', contents=prompt)
    return resposta.text.strip()

# Cérebro 2: Para quem NÃO tem experiência (Foco no Objetivo)
def melhorar_objetivo_ia(texto_bruto):
    client = genai.Client(api_key=CHAVE_API_GEMINI.strip())
    prompt = f"""
    Você é um especialista em RH ajudando um candidato em busca do primeiro emprego.
    O candidato escreveu o seguinte objetivo profissional (que pode conter erros ortográficos ou estar muito informal):
    "{texto_bruto}"
    
    Sua tarefa:
    1. Corrija qualquer erro ortográfico ou gramatical.
    2. Torne o texto mais profissional, proativo e claro, demonstrando vontade de aprender.
    3. Mantenha o texto curto e direto (máximo de 2 a 3 linhas).
    4. Devolva APENAS o texto final pronto para o currículo, sem aspas ou introduções.
    """
    resposta = client.models.generate_content(model='gemini-flash-latest', contents=prompt)
    return resposta.text.strip()


# --- 4. INTERFACE STREAMLIT ---
st.set_page_config(page_title="DevStart - Gerador de Currículo", layout="wide")

# --- TELA DE BOAS-VINDAS E APRESENTAÇÃO ---
st.title("🚀 Bem-vindo ao DevStart Currículos")
st.info("""
**Nosso objetivo é ajudar você a estruturar da melhor forma o seu currículo!**

Sabemos que grandes empresas utilizam Inteligência Artificial para fazer a triagem de candidatos (sistemas ATS). 
Por isso, criamos esta ferramenta gratuita para formatar o seu currículo de um jeito limpo e otimizado, 
garantindo que os robôs dos recrutadores consigam ler suas informações perfeitamente e destacar o seu potencial.
""")

st.markdown("---")

# --- A GRANDE ESCOLHA (DIVISÃO DE JORNADA) ---
st.subheader("Para começarmos, você possui experiência profissional?")

opcoes_jornada = [
    "Sim, possuo experiência profissional", 
    "Não, estou em busca do meu primeiro emprego"
]

escolha_jornada = st.radio(
    "Selecione uma opção:", 
    opcoes_jornada,
    label_visibility="collapsed"
)

st.markdown("---")
st.write("### Preencha seus dados abaixo:")

# --- DADOS PESSOAIS (COMUM) ---
st.subheader("👤 1. Dados Pessoais e Contato")
col_p1, col_p2 = st.columns(2)
with col_p1:
    nome = st.text_input("Nome Completo", placeholder="Ex: Nome Sobrenome")
    email = st.text_input("E-mail", placeholder="Ex: fulano@gmail.com")
    telefone = st.text_input("Telefone (WhatsApp)", placeholder="(11) 99999-9999")
with col_p2:
    idade = st.number_input("Idade", min_value=14, max_value=100, value=20)
    cidade = st.text_input("Cidade/UF", placeholder="Ex: São Paulo - SP")
    linkedin = st.text_input("LinkedIn (Opcional)", placeholder="linkedin.com/in/seu-perfil")

# --- FORMAÇÃO E CURSOS (COMUM) ---
st.subheader("🎓 2. Formação e Cursos")
col_f1, col_f2 = st.columns(2)
with col_f1:
    local_estudo = st.text_input("Universidade/Escola", placeholder="Ex: Universidade Cruzeiro do Sul")
    status_estudo = st.selectbox("Status", ["Concluído", "Em andamento", "Trancado", "Incompleto"])
with col_f2:
    curso_estudo = st.text_input("Curso / Nível", placeholder="Ex: Ciência da Computação ou Ensino Médio")
    data_conclusao = st.text_input("Data de Conclusão / Previsão", placeholder="Ex: Dezembro/2028 ou 2020")

certificacoes = st.text_area("Cursos Extras (um por linha) - Opcional", placeholder="Ex: Pacote Office - Fundação Bradesco\nInglês Básico - Fisk")

# --- SEÇÃO DINÂMICA (DEPENDE DA ESCOLHA) ---
tem_experiencia = (escolha_jornada == opcoes_jornada[0])

exp_texto = ""
objetivo = ""
soft_skills = ""

if tem_experiencia:
    st.subheader("💼 3. Experiência Profissional")
    st.write("Escreva como se estivesse conversando. Ex: 'Trabalhei de atendente de janeiro a agosto de 2024 na loja X, eu fechava caixa e ajudava clientes no zap'. A IA vai transformar isso em algo profissional!")
    exp_texto = st.text_area("Descreva suas experiências:", height=150)
else:
    st.subheader("🎯 3. Objetivo e Competências")
    st.write("Como você busca o primeiro emprego, vamos focar no seu perfil e vontade de aprender. Escreva seu objetivo de forma simples e nossa Inteligência Artificial deixará profissional!")
    objetivo = st.text_input("Qual o seu objetivo profissional?", placeholder="Ex: Busco minha primeira oportunidade na área de administração...")
    soft_skills = st.text_area(
        "Quais são suas competências? (Soft Skills - Separe por vírgula ou Enter)", 
        placeholder="Ex: Trabalho em equipe, Comunicação clara, Proatividade, Organização...",
        height=100
    )

# --- BOTÃO DE GERAR ---
st.markdown("---")
if st.button("✨ Gerar Currículo DevStart", use_container_width=True):
    if not nome:
        st.error("Por favor, preencha pelo menos o seu Nome Completo.")
    elif not CHAVE_API_GEMINI and (exp_texto.strip() != "" or objetivo.strip() != ""):
        # Só dá erro de chave se a pessoa realmente digitou algo para a IA processar
        st.error("Erro: A chave da API não foi encontrada nas configurações (Secrets) do Streamlit.")
    else:
        with st.spinner("Construindo o seu currículo (A Inteligência Artificial está trabalhando)..."):
            texto_experiencia_final = exp_texto
            objetivo_final = objetivo
            
            # --- ACIONA A IA PARA EXPERIÊNCIA ---
            if tem_experiencia and exp_texto.strip() != "":
                try:
                    texto_experiencia_final = melhorar_experiencia_ia(exp_texto)
                except Exception as e:
                    st.error(f"Erro ao conectar com a IA (Experiência). (Detalhes: {e})")
                    
            # --- ACIONA A IA PARA O OBJETIVO ---
            elif not tem_experiencia and objetivo.strip() != "":
                try:
                    objetivo_final = melhorar_objetivo_ia(objetivo)
                except Exception as e:
                    st.error(f"Erro ao conectar com a IA (Objetivo). (Detalhes: {e})")

            # Montando a estrutura para o PDF
            dados_usuario = {
                "nome": nome, "email": email, "telefone": telefone, "cidade": cidade, "idade": idade, "linkedin": linkedin,
                "objetivo": objetivo_final, # Passando o objetivo processado pela IA
                "soft_skills": soft_skills,
                "formacao_local": local_estudo,
                "formacao_curso": curso_estudo,
                "formacao_status": status_estudo,
                "formacao_data": data_conclusao,
                "tem_experiencia": tem_experiencia,
                "experiencia_formatada": texto_experiencia_final,
                "cursos": certificacoes.split('\n')
            }
            
            # Gera o PDF
            arquivo = gerar_curriculo_ats(dados_usuario)
            
            st.success("Currículo pronto!")
            with open(arquivo, "rb") as f:
                st.download_button("📥 Baixar Currículo em PDF", data=f, file_name=arquivo, mime="application/pdf")