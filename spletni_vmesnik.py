import bottle
from sqlite3 import IntegrityError
from model import LoginError,  Igre, Podjetje, Platforma

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
        podatki_o_igri = Igre.podatki_o_igri(igra)
    )

@bottle.get('/igre/<podjetje>/')
def podjetje(podjetje):
    return bottle.template(
        'html/podjetje.html',
        podjetje = podjetje,
        podatki_o_podjetju = Podjetje.podatki_o_podjetju(podjetje)
    )

@bottle.get('/igre/<platforma>/')
def platforma(platforma):
    return bottle.template(
        'html/platforma.html',
        platforma = platforma,
        podatki_o_platformi = Platforma.podatki_o_platformi(platforma)
    )

@bottle.get('/isci/')
def iskanje():
    iskalni_niz = bottle.request.query.getunicode('iskalni_niz')
    igre = Igre.poisci(iskalni_niz)
    return bottle.template(
        'html/iskanje.html',
        iskalni_niz = iskalni_niz,
        igre = igre
    )

@bottle.get('/glej_vse_igre/')
def glej_vse_igre():
    return bottle.template(
        'html/glej_vse_igre.html',
        glej_vse_igre=Igre.glej_vse_igre()
    )


bottle.run(debug=True, reloader=True)