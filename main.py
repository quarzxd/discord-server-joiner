# ┌∩┐(◣_◢)┌∩┐
import base64
import json
import uuid
import os
from colorama import Fore
import tls_client

session = tls_client.Session(client_identifier="chrome_138", random_tls_extension_order=True, ja3_string="771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-5-10-11-13-16-18-23-27-35-43-45-51-17613-65037-65281,4588-29-23-24,0", h2_settings={"HEADER_TABLE_SIZE": 65536, "ENABLE_PUSH": 0, "INITIAL_WINDOW_SIZE": 6291456, "MAX_HEADER_LIST_SIZE": 262144}, h2_settings_order=["HEADER_TABLE_SIZE", "ENABLE_PUSH", "INITIAL_WINDOW_SIZE", "MAX_HEADER_LIST_SIZE"], supported_signature_algorithms=["ecdsa_secp256r1_sha256", "rsa_pss_rsae_sha256", "rsa_pkcs1_sha256", "ecdsa_secp384r1_sha384", "rsa_pss_rsae_sha384", "rsa_pkcs1_sha384", "rsa_pss_rsae_sha512", "rsa_pkcs1_sha512"], supported_versions=["TLS_1_3", "TLS_1_2"], key_share_curves=["GREASE", "X25519MLKEM768", "X25519", "secp256r1", "secp384r1"], pseudo_header_order=[":method", ":authority", ":scheme", ":path"], connection_flow=15663105, priority_frames=[])

C = {
    "green": "#65fb07",
    "red": "#Fb0707",
    "yellow": "#FFCD00",
    "magenta": "#b207f5",
}

class MockConsole:
    def log(self, status, color, token, message=""):
        print(f"[{status}] {token} {message}")

console = MockConsole()

class MockMenu:
    def run(self, func, args):
        for arg in args:
            func(*arg)

Menu = MockMenu

def get_headers(token):
    return {
        "authorization": token,
        "content-type": "application/json",
    }

def load_tokens():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_file = os.path.join(script_dir, "tokens.txt")
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def joiner(invite, tokens):
    try:
        params = {
            "inputValue": f"https://discord.gg/{invite}",
            "with_counts": "true",
            "with_expiration": "true",
            "with_permissions": "true",
        }

        for token in tokens:
            response = session.get(
                f"https://discord.com/api/v9/invites/{invite}",
                headers=get_headers(token),
                params=params
            )

            match response.status_code:
                case 200:
                    invite_info = response.json()
                    break
                case 404:
                    console.log("Failed", C["red"], "Invalid or expired invite")
                    return

        guild_name = invite_info["guild"]["name"]
        guild_id = invite_info["guild"]["id"]
        channel_id = invite_info["channel"]["id"]
        channel_type = invite_info["channel"]["type"]

        join = {
            "location": "Join Guild",
            "location_guild_id": guild_id,
            "location_channel_id": channel_id,
            "location_channel_type": channel_type
        }
        context = base64.b64encode(json.dumps(join).encode()).decode()

        def join_server(token):
            try:
                headers = get_headers(token)
                headers["X-Context-Properties"] = context

                payload = {
                    "session_id": uuid.uuid4().hex
                }

                resp = session.post(
                    f"https://discord.com/api/v9/invites/{invite}",
                    headers=headers,
                    json=payload
                )

                match resp.status_code:
                    case 200:
                        console.log("Joined", C["green"], f"{Fore.RESET}{token[:25]}.{Fore.LIGHTCYAN_EX}**", guild_name)
                    case 400:
                        console.log("Captcha", C["yellow"], f"{Fore.RESET}{token[:25]}.{Fore.LIGHTCYAN_EX}**", guild_name)
                    case 429:
                        console.log("Cloudflare", C["magenta"], f"{Fore.RESET}{token[:25]}.{Fore.LIGHTCYAN_EX}**", guild_name)
                    case _:
                        console.log("Failed", C["red"], f"{Fore.RESET}{token[:25]}.{Fore.LIGHTCYAN_EX}**", resp.json()["message"])
            except Exception as e:
                console.log("Failed", C["red"], f"{Fore.RESET}{token[:25]}.{Fore.LIGHTCYAN_EX}**", e)

        args = [(token,) for token in tokens]
        menu = Menu()
        menu.run(join_server, args)
    except Exception as e:
        console.log("Failed", C["red"], "Failed to get invite info", e)

if __name__ == "__main__":
    tokens_list = load_tokens()
    if tokens_list:
        invite = input("Enter invite code: ")
        joiner(invite, tokens_list)
    else:
        print("No tokens found in tokens.txt")
