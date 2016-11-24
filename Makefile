default: buildout

buildout: bin/buildout
	bin/buildout
	bin/pip install isort

bin/buildout:
	virtualenv .
	bin/pip install -r requirements.txt
	bin/buildout bootstrap

clean:
	rm -rf bin/* lib/*
