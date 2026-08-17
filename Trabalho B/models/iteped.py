# Classe de item do pedido.

class Titeped:
    # Variaveis que representam os campos da tabela
    seqiteped = None
    codped = None
    numite = None
    codpro = None
    qtdite = None

    def __init__(self, conn):
        self.conn = conn

    # Le os dados pela chave
    def le(self, p_seqiteped: int):
        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                    SELECT {self.colunas_do_select()}
                      FROM iteped
                     WHERE seqiteped = %s
                """,
                (p_seqiteped,),
            )
            row = cur.fetchone()

        if row:
            self.carrega_do_dataset(row)
            return True

        return False

    # Carrega os dados do dataset para os atributos da classe
    def carrega_do_dataset(self, row):
        self.seqiteped = row["seqiteped"]
        self.numite = row["numite"]
        self.codpro = row["codpro"]
        self.qtdite = row["qtdite"]
        self.codped = row["codped"]

    # Adiciona ao SQL SELECT <coluna1>,<coluna2>, etc
    def colunas_do_select(self):
        return " iteped.seqiteped, iteped.numite, iteped.codpro, iteped.qtdite, iteped.codped "
