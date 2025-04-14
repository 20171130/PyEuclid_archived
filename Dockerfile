FROM python:3.11
RUN mkdir /PyEuclid
COPY ./ /PyEuclid
WORKDIR /PyEuclid
RUN pip install -r requirements.txt
CMD python test_single.py