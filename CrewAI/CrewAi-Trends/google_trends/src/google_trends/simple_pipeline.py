import os
import datetime as dt
import json
from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv

try:
    # Carrega .env local do pacote e variáveis do ambiente ANTES de importar as ferramentas
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)
    load_dotenv()
except Exception:
    # Segue sem falhar se dotenv não estiver disponível
    pass

# Ferramentas customizadas (agora com ambiente carregado)
from google_trends.tools.custom_tool import SERPTrendsTool, SERPNewsTool


def _ensure_output_dir() -> Path:
    """
    Garante a existência do diretório de saída 'resultado' ao lado do pacote
    e retorna o caminho.
    """
    out_dir = Path(__file__).parent / "resultado"
    out_dir.mkdir(exist_ok=True)
    return out_dir


def _summarize_with_llm(sector: str, trends_and_news: List[Dict]) -> str:
    """
    Gera um resumo em português usando o endpoint OpenAI-compatível configurado
    via variáveis OPENAI_API_BASE, OPENAI_API_KEY e OPENAI_MODEL_NAME.

    Este método utiliza Chat Completions e NÃO depende de function/tool calling,
    garantindo compatibilidade com servidores locais (ex.: Ollama com proxy compatível).
    """
    from openai import OpenAI

    base_url = os.getenv("OPENAI_API_BASE")
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL_NAME")

    if not base_url or not api_key or not model:
        raise RuntimeError("Variáveis OPENAI_API_BASE, OPENAI_API_KEY e OPENAI_MODEL_NAME são obrigatórias para o resumo.")

    client = OpenAI(base_url=base_url, api_key=api_key)

    # Monta um resumo estruturado em Markdown
    bullets = []
    for item in trends_and_news:
        kw = item.get("keyword")
        articles = item.get("articles", [])
        if not kw:
            continue
        bullets.append(f"- Palavra-chave: {kw}")
        for art in articles[:3]:
            title = art.get("title")
            source = art.get("source")
            link = art.get("link")
            bullets.append(f"  - {title} ({source}) — {link}")

    content = (
        "Você é um analista de inteligência de mercado em português. "
        "Com base nas palavras-chave e notícias coletadas para o setor '" + sector + "', "
        "elabore um resumo breve (5–10 linhas) destacando tendências relevantes, riscos e oportunidades. "
        "Use um tom claro e objetivo. Em seguida, liste as fontes em bullet points.\n\n"
        "Fontes coletadas:\n" + "\n".join(bullets)
    )

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um assistente que escreve em português do Brasil."},
            {"role": "user", "content": content},
        ],
        temperature=0.2,
    )

    return resp.choices[0].message.content or ""


def _format_table_md(setor: str, trends: List[Dict], news: List[Dict]) -> str:
    """
    Gera uma tabela Markdown no padrão solicitado.

    Colunas: Palavra-chave | Tipo | Título | Fonte | Link | Data/Hora | Dia | Resumo

    Observações: seção ao final.
    """
    # Hora e identificação da coleta (08:00 => Coleta 1, 12:00 => Coleta 2)
    now = dt.datetime.now()
    hora = now.strftime("%H:%M")
    coleta = "Coleta 1" if now.hour < 10 else ("Coleta 2" if now.hour < 13 else "Coleta")
    dia_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][now.weekday()]

    header = f"# Análise de Tendências em {setor} ({coleta} - {hora})\n\n"

    # Índice rápido por keyword para o 'type' (top/rising)
    type_by_kw = {}
    for t in trends:
        kw = t.get("keyword")
        typ = t.get("type")
        if kw:
            type_by_kw[kw] = typ or "top"

    # Índice de notícias por keyword
    news_by_kw = {n.get("keyword"): n.get("articles", []) for n in news}

    lines = [header]
    lines.append("| Palavra-chave | Tipo | Título | Fonte | Link | Data/Hora | Dia | Resumo |\n")
    lines.append("|---|---|---|---|---|---|---|---|\n")

    for kw, typ in type_by_kw.items():
        articles = news_by_kw.get(kw, [])
        if not articles:
            # Linha sem notícia encontrada
            lines.append(f"| {kw} | {typ} | — | — | — | {hora} | {dia_semana} | — |\n")
            continue
        for art in articles:
            title = art.get("title") or "—"
            fonte = art.get("source") or "—"
            link = art.get("link") or "—"
            data_str = art.get("date") or hora
            resumo = title if title != "—" else "—"
            lines.append(
                f"| {kw} | {typ} | {title} | {fonte} | {link} | {data_str} | {dia_semana} | {resumo} |\n"
            )

    lines.append("\n\nObservações\n\nNenhuma observação adicional neste momento.\n")
    return "".join(lines)


def _send_email_with_smtp(file_path: Path) -> None:
    """
    Envia o arquivo Markdown por e-mail via SMTP.

    Variáveis esperadas no .env:
    - SMTP_HOST, SMTP_PORT
    - SMTP_USER, SMTP_PASSWORD
    - EMAIL_FROM, EMAIL_TO (lista separada por vírgulas), EMAIL_SUBJECT (opcional)
    """
    import smtplib
    from email.message import EmailMessage

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    email_from = os.getenv("EMAIL_FROM")
    email_to = os.getenv("EMAIL_TO")
    subject = os.getenv("EMAIL_SUBJECT", "Relatório de Tendências e Notícias")

    if not (smtp_host and smtp_user and smtp_pass and email_from and email_to):
        # Se faltarem variáveis, não enviar.
        return

    recipients = [e.strip() for e in email_to.split(",") if e.strip()]

    msg = EmailMessage()
    msg["From"] = email_from
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.set_content("Segue em anexo o relatório gerado automaticamente.")

    # Lê o conteúdo Markdown e converte para HTML para enviar no corpo do e-mail
    content_md = file_path.read_text(encoding="utf-8")
    try:
        # Importa localmente para evitar dependência global quando a função não é usada
        import markdown  # type: ignore

        # Converte Markdown em HTML com suporte a tabelas e código
        html_inner = markdown.markdown(
            content_md,
            extensions=["tables", "fenced_code"],
            output_format="html5",
        )

        # Aplica um template simples com estilos básicos para boa leitura em clientes de e-mail
        html_body = f"""
        <html>
          <head>
            <meta charset='utf-8'>
            <style>
              body {{ font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; line-height: 1.5; color: #222; }}
              h1, h2, h3 {{ color: #111; margin-top: 1.2em; }}
              table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
              th, td {{ border: 1px solid #ddd; padding: 8px; }}
              th {{ background: #f3f3f3; text-align: left; }}
              code, pre {{ background: #f6f8fa; padding: 2px 4px; border-radius: 4px; }}
              pre {{ padding: 8px; overflow: auto; }}
              a {{ color: #0b5fff; }}
            </style>
          </head>
          <body>
            {html_inner}
          </body>
        </html>
        """

        # Define corpo texto simples e alternativa HTML
        msg.set_content("Seu cliente de e-mail não suporta HTML. Veja o relatório em um navegador.")
        msg.add_alternative(html_body, subtype="html")
    except Exception:
        # Se falhar a conversão, envia o Markdown em anexo como fallback
        msg.set_content("Segue em anexo o relatório em Markdown.")
        msg.add_attachment(content_md, subtype="markdown", filename=file_path.name)

    # Tentar primeiro STARTTLS (porta 587)
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as s:
            s.starttls()
            s.login(smtp_user, smtp_pass)
            s.send_message(msg)
            print(f"✅ E-mail enviado com sucesso via STARTTLS (porta {smtp_port})")
    except Exception as e:
        print(f"❌ Falha com STARTTLS: {e}")
        # Tentar SSL na porta 465 como fallback
        print("🔄 Tentando SSL na porta 465...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(smtp_user, smtp_pass)
            s.send_message(msg)
            print("✅ E-mail enviado com sucesso via SSL (porta 465)")


def _send_email_via_api(file_path: Path) -> None:
    """
    Envia o arquivo Markdown por e-mail via API HTTP.

    Suporte inicial:
    - SendGrid: requer SENDGRID_API_KEY
      Usa endpoint POST https://api.sendgrid.com/v3/mail/send
    - Mailgun: requer MAILGUN_API_KEY e MAILGUN_DOMAIN
      Usa endpoint POST https://api.mailgun.net/v3/{domain}/messages

    Variáveis comuns:
    - EMAIL_FROM
    - EMAIL_TO (lista separada por vírgulas)
    - EMAIL_SUBJECT (opcional)
    """
    provider = (os.getenv("EMAIL_API_PROVIDER") or "").strip().lower()
    email_from = os.getenv("EMAIL_FROM")
    email_to = os.getenv("EMAIL_TO")
    subject = os.getenv("EMAIL_SUBJECT", "Relatório de Tendências e Notícias")

    if not (provider and email_from and email_to):
        return

    recipients = [e.strip() for e in email_to.split(",") if e.strip()]
    content = file_path.read_text(encoding="utf-8")

    try:
        if provider == "sendgrid":
            import requests
            api_key = os.getenv("SENDGRID_API_KEY")
            if not api_key:
                return
            payload = {
                "personalizations": [{"to": [{"email": r} for r in recipients]}],
                "from": {"email": email_from},
                "subject": subject,
                "content": [{"type": "text/plain", "value": content}],
            }
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            resp = requests.post("https://api.sendgrid.com/v3/mail/send", headers=headers, data=json.dumps(payload), timeout=15)
            # SendGrid retorna 202 em sucesso
            if resp.status_code not in (200, 202):
                # não falhar pipeline; apenas não enviar
                return
        elif provider == "mailgun":
            import requests
            api_key = os.getenv("MAILGUN_API_KEY")
            domain = os.getenv("MAILGUN_DOMAIN")
            if not (api_key and domain):
                return
            url = f"https://api.mailgun.net/v3/{domain}/messages"
            data = {
                "from": email_from,
                "to": ", ".join(recipients),
                "subject": subject,
                "text": content,
            }
            resp = requests.post(url, auth=("api", api_key), data=data, timeout=15)
            if resp.status_code not in (200, 202):
                return
        else:
            # Provedor desconhecido
            return
    except Exception:
        # Não interromper a pipeline em caso de erro de envio
        return


def run_simple(inputs: Dict) -> Path:
    """
    Executa a pipeline simples, sem CrewAI, para ambientes onde o LLM
    OpenAI-compatível não suporta function/tool calling.

    Etapas:
    1) Coleta tendências com SERPTrendsTool.
    2) Busca notícias com SERPNewsTool para cada palavra-chave.
    3) Resume com LLM via Chat Completions.
    4) Salva Markdown em resultado/Noticias.md.
    """
    setor = inputs.get("Setor", "Autos")

    # 1) Tendências
    trends = SERPTrendsTool()._run(categoria=setor, top_n=10, rising_n=10)
    keywords = [t["keyword"] for t in trends if t.get("keyword")]

    # 2) Notícias
    news = SERPNewsTool()._run(keywords=keywords, max_articles=3)

    # 3) Resumo geral
    resumo = _summarize_with_llm(sector=setor, trends_and_news=news)

    # 4) Tabela padronizada
    tabela_md = _format_table_md(setor=setor, trends=trends, news=news)

    # 5) Arquivo Markdown
    out_dir = _ensure_output_dir()
    out_path = out_dir / "Noticias.md"
    md = [
        tabela_md,
        "\n\n## Resumo Geral\n\n",
        resumo,
        "\n",
    ]
    out_path.write_text("".join(md), encoding="utf-8")

    # 6) Envio por e-mail (opcional): modo API ou SMTP
    email_mode = (os.getenv("EMAIL_MODE") or "smtp").strip().lower()
    if email_mode == "api":
        _send_email_via_api(out_path)
    else:
        _send_email_with_smtp(out_path)
    return out_path