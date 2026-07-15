FROM python:3.10.14
EXPOSE 8080
WORKDIR /
COPY . ./
RUN pip install -r requirements.txt
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8080", "--server.address=0.0.0.0"]