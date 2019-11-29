default: buildout

buildout: bin/buildout
	bin/buildout
	bin/pip install isort

bin/buildout:
	virtualenv .
	bin/pip install -r requirements.txt

clean:
	rm -rf bin/* lib/*
