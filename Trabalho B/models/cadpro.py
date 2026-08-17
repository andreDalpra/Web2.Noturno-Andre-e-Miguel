# Classe de produto.

class Tcadpro:
    # Variaveis que representam os campos da tabela
    codpro = None
    despro = None
    vlrpro = None

    def __init__(self, conn):
        self.conn = conn

    # Le os dados pela chave
    def le(self, p_codpro: int):
        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                    SELECT {self.colunas_do_select()}
                      FROM cadpro
                     WHERE codpro = %s
                """,
                (p_codpro,),
            )
            row = cur.fetchone()

        if row:
            self.carrega_do_dataset(row)
            return True

        return False

    # Carrega os dados do dataset para os atributos da classe
    def carrega_do_dataset(self, row):
        self.codpro = row["codpro"]
        self.despro = row["despro"]
        self.vlrpro = row["vlrpro"]

    # Adiciona ao SQL SELECT <coluna1>,<coluna2>, etc
    def colunas_do_select(self):
        return " cadpro.codpro, cadpro.despro, cadpro.vlrpro "
