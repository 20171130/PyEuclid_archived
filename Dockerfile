FROM python:3.11
RUN git clone https://github.com/anonymous/Euclid-Omni
WORKDIR /Euclid-Omni
RUN pip install .
CMD python tests/test_single.py --show-proof
