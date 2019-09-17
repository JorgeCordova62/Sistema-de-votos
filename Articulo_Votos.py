import time
import redis
conn = redis.Redis(host='localhost', port=6379, db=0)


#Prepara nuestras constantes.
ONE_WEEK_IN_SECONDS = 7 * 86400
VOTE_SCORE = 432

def article_vote(conn, user, article):
    #Calcule el tiempo límite para votar.
    cutoff = time.time() - ONE_WEEK_IN_SECONDS

    #Verifique si aún se puede votar el artículo (podríamos usar el 
    # artículo HASH aquí, pero los puntajes se devuelven como flotantes 
    # para que no tengamos que emitirlo).
   
    if conn.zscore('time:', article) < cutoff:
        return

     # Obtenga la parte de identificación del artículo: 
     # identificador de identificación.
    article_id = article.partition(':')[-1]

    #Si el usuario no ha votado antes por este artículo, incremente la
    #  puntuación del artículo y el recuento de votos.
    if conn.sadd('voted:' + article_id, user):
        conn.zincrby('score:', article, VOTE_SCORE)
        conn.hincrby(article, 'votes', 1)


def post_article(conn, user, title, link):
    article_id = str(conn.incr('article:')) #Genera un nuevo id de articulo
    voted = 'voted:' + article_id
    conn.sadd(voted, user)
    conn.expire(voted, ONE_WEEK_IN_SECONDS) #Configura para que el voto del articulo caduque en una semana
    now = time.time()  #Optiene la hora en ese momento
    article = 'article:' + article_id 
    conn.hmset(article, {
        'title': title,
        'link': link,
        'poster': user,
        'time': now,
        'votes': 1,
    })
    conn.zadd('score:', article, now + VOTE_SCORE)
    conn.zadd('time:', article, now)
    return article_id