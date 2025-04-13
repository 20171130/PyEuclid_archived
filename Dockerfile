FROM python:3.11
RUN mkdir /PyEuclid
COPY ./requirements.txt /PyEuclid/requirements.txt
RUN pip install -r requirements.txt
CMD python test_single.py