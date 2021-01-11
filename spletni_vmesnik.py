import bottle
from sqlite3 import IntegrityError
from model import LoginError,  Igre

@bottle.get('/')
def glavna_stran():
    return bottle.template(
        'html/glavna_stran.html',
        najnovejse_igre = Igre.najnovejse_igre()
    )

@bottle.get('/<igra>/')
def igra(igra):
    return bottle.template(
        'html/igra.html',
        igra = igra,
        podatki_o_igri=Igre.podatki_o_igri(igra)
    )



bottle.run(debug=True, reloader=True)