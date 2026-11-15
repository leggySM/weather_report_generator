def get_forecast():
    import requests
    params = {"latitude": -33.92, "longitude": 18.42, "current_weather": "true", "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
    "timezone": "auto"}
    try:
        r = requests.get("https://api.open-meteo.com/v1/forecast", params = params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.Timeout:
        print("The server took too damn long to respond!")
        raise SystemExit
    except requests.exceptions.ConnectionError:
        print("Failed to connect (trash WiFi?)")
        raise SystemExit
    except requests.exceptions.HTTPError as e:
        print(f"DENIED: {e}")
        raise SystemExit
    except requests.exceptions.RequestException as u:
        print(f"idk what happened mane, try again or somethin: {u}")
        raise SystemExit
    return data

def build_pdf(data, path):
    from fpdf import FPDF
    units = data['daily_units']
    tUnit = units['temperature_2m_max']
    pUnit = units['precipitation_sum']
    daily = data['daily']
    pdf = FPDF()
    hot = max(daily['temperature_2m_max'])
    hotDay = daily["time"][daily["temperature_2m_max"].index(hot)]

    pdf.add_page()
    pdf.set_font("Helvetica", size=16)
    pdf.cell(0, 10, f"Cape Town Weather Report ({daily['time'][0]})", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=12)

    for day, high, low, rain in zip(
        daily['time'],
        daily['temperature_2m_max'],
        daily['temperature_2m_min'],
        daily['precipitation_sum']
        ):
        pdf.cell(0, 6, f"{day}: {low}{tUnit} to {high}{tUnit} with {rain}{pUnit} precipitation", new_x="LMARGIN", new_y="NEXT")

    pdf.ln()
    pdf.cell(0, 8, f"HOTTEST DAY OF THE WEEK: {hotDay}")
    pdf.output(path)

def send_email(path):
    import smtplib
    from email.message import EmailMessage
    from config import EMAIL, appPassword
    try:
        msg = EmailMessage()
        msg["Subject"] = "Cape Town Weekly Weather Report"
        msg["From"] = EMAIL
        msg["To"] = EMAIL
        msg.set_content("Your weather report is attached.")
    
        with open(path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="report.pdf")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, appPassword)
            server.send_message(msg)
    except smtplib.SMTPAuthenticationError:
        print("Incorrect password; could not authenticate.")
    except (smtplib.SMTPException, OSError) as e:
        print(f"OS Error: {e}")

if __name__ == "__main__":
    report = "report.pdf"
    build_pdf(get_forecast(), report)
    send_email(report)