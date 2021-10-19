from handlers.request_handler import RequestHandler


class HostSessionHandler(RequestHandler):

    def get_message_prefix(self) -> str:
        return "h"

    def handle_message(self, message: str, address: tuple):
        session_name, player_name, max_players, password = self.parse_host_request(message, address)
        ip, port = address
        self.logger.debug("Received request from player %s to host session %s for max %s players. Source: %s:%s",
                          player_name, session_name, max_players, ip, port)

        self.check_host_session(session_name, address)

        self.active_sessions[session_name] = Session(session_name, max_players, Player(player_name, ip, port), password)
        self.logger.info("Created session %s (max %s players)", session_name, max_players)
        self.send_session_info(address, self.active_sessions[session_name])

