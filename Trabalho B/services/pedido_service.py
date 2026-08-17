from models.cadped import Tcadped


class PedidoService:
    def __init__(self, conn):
        self.conn = conn
        self._cadped = None

    def cadastra_pedido(self, p_cadped: Tcadped):
        p_cadped.conn = self.conn

        # Valida os dados do pedido
        op_infmsg = p_cadped.valida()
        if op_infmsg:
            return op_infmsg

        op_infmsg = p_cadped.insere()
        if op_infmsg:
            return op_infmsg

        self.cadped = p_cadped
        return ""

    def busca_pedido(self, p_codped: int):
        if not self.cadped.le(p_codped):
            return None

        return self.cadped

    def remove_pedido(self, p_codped: int):
        pedido = self.busca_pedido(p_codped)

        if not pedido:
            return f"Pedido nao encontrado com o codigo {p_codped}."

        return self.cadped.remove()

    @property
    def cadped(self):
        if not self._cadped:
            self._cadped = Tcadped(self.conn)
        return self._cadped

    @cadped.setter
    def cadped(self, value):
        self._cadped = value
