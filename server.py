import http.server
import socketserver
import json
import os
import time

PORT = int(os.environ.get('PORT', 3003))
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")
COMBOS_FILE = os.path.join(DATA_DIR, "combos.json")
FLAVORS_FILE = os.path.join(DATA_DIR, "flavors.json")
DRINKS_FILE = os.path.join(DATA_DIR, "drinks.json")
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.json")
REWARDS_FILE = os.path.join(DATA_DIR, "rewards.json")

DEFAULT_ORDERS = [
  {
    "id": "REI-101",
    "clientName": "Cliente Centro BC",
    "clientPhone": "47988802254",
    "address": "Av. Brasil, 1500 - Centro, Balneário Camboriú",
    "items": "1x Oferta 01 (Pizza Calabresa Acebolada / Frango com Catupiry, Borda Catupiry) + Refri Kuat 2L",
    "total": 60.90,
    "paymentMethod": "PIX",
    "status": "EM_PREPARO",
    "date": "Hoje, 19:15"
  }
]

DEFAULT_COMBOS = [
  {
    "id": "combo_1",
    "name": "Oferta 01: 1 Pizza Grande + Refri Kuat 2L",
    "desc": "1 Pizza Grande (8 Fatias) + 1 Refrigerante Kuat 2 Litros",
    "price": 54.90,
    "pizzasCount": 1,
    "badge": "OFERTA 01"
  },
  {
    "id": "combo_2",
    "name": "Oferta 02: 2 Pizzas Grandes + Refri Kuat 2L",
    "desc": "2 Pizzas Grandes (8 Fatias cada) + 1 Refrigerante Kuat 2 Litros",
    "price": 99.90,
    "pizzasCount": 2,
    "badge": "OFERTA 02 - MAIS VENDIDO"
  }
]

DEFAULT_FLAVORS = [
  { "id": "flav_1", "name": "Mussarela", "desc": "Molho de tomate e mussarela.", "price": 49.90 },
  { "id": "flav_2", "name": "Mussaalho", "desc": "Molho de tomate, mussarela e alho frito.", "price": 49.90 },
  { "id": "flav_3", "name": "Mussarela e milho", "desc": "Molho de tomate, mussarela e milho verde.", "price": 49.90 },
  { "id": "flav_4", "name": "Bacon", "desc": "Molho de tomate, mussarela e bacon.", "price": 49.90 },
  { "id": "flav_5", "name": "Bacon e milho", "desc": "Molho de tomate, mussarela, bacon e milho verde.", "price": 49.90 },
  { "id": "flav_6", "name": "Calabresa", "desc": "Molho de tomate, mussarela e calabresa fatiada.", "price": 49.90 },
  { "id": "flav_7", "name": "Calabresa acebolada", "desc": "Molho de tomate, mussarela, calabresa fatiada e cebola.", "price": 49.90 },
  { "id": "flav_8", "name": "Frango com catupiry", "desc": "Molho de tomate, mussarela, frango desfiado temperado e catupiry.", "price": 49.90 },
  { "id": "flav_9", "name": "Portuguesa", "desc": "Molho de tomate, presunto, mussarela, tomate, pimentão, cebola, ovo e orégano.", "price": 49.90 },
  { "id": "flav_10", "name": "Bauru", "desc": "Molho de tomate, mussarela, presunto, tomate e catupiry.", "price": 49.90 }
]

DEFAULT_DRINKS = [
  { "id": "drk_1", "name": "🥤 Guaraná Kuat 2 Litros", "price": 10.00, "icon": "🍾" },
  { "id": "drk_2", "name": "🥤 Coca-Cola 2 Litros", "price": 12.00, "icon": "🍾" },
  { "id": "drk_3", "name": "🥤 Coca-Cola Lata 350ml", "price": 6.00, "icon": "🥤" },
  { "id": "drk_4", "name": "🍋 Guaraná Antarctica Lata 350ml", "price": 6.00, "icon": "🥤" },
  { "id": "drk_5", "name": "💧 Água Mineral sem Gás 500ml", "price": 4.00, "icon": "💧" }
]

DEFAULT_CUSTOMERS = [
  {
    "phone": "47988802254",
    "name": "Cliente Pizzaria BC",
    "email": "cliente@reidosreis.com.br",
    "password": "123",
    "points": 120,
    "createdAt": "2026-08-15"
  }
]

DEFAULT_REWARDS = [
  { "id": "rew_1", "name": "🧀 Borda Recheada Grátis", "points": 40, "desc": "Borda recheada de Catupiry ou Cheddar grátis na sua pizza", "type": "extra", "value": 6.00, "icon": "🧀" },
  { "id": "rew_2", "name": "🥤 Refri Kuat 2 Litros Grátis", "points": 60, "desc": "1x Refrigerante Kuat 2 Litros", "type": "drink", "value": 10.00, "icon": "🥤" },
  { "id": "rew_3", "name": "🏷️ Cupom de R$ 15,00 de Desconto", "points": 100, "desc": "Desconto de R$ 15,00 no total do pedido", "type": "discount", "value": 15.00, "icon": "🏷️" },
  { "id": "rew_4", "name": "🍕 1 Pizza Grande Grátis", "points": 200, "desc": "1x Pizza Grande (8 Fatias) de qualquer sabor tradicional", "type": "pizza", "value": 49.90, "icon": "🍕" }
]

def load_json_file(filepath, default_data):
    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        return default_data
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default_data

def save_json_file(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class ReiDosReisRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Bypass-Tunnel-Reminder', '1')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def log_message(self, format, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/orders':
            orders = load_json_file(ORDERS_FILE, DEFAULT_ORDERS)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(orders, ensure_ascii=False).encode('utf-8'))
            return

        if self.path == '/api/combos':
            combos = load_json_file(COMBOS_FILE, DEFAULT_COMBOS)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(combos, ensure_ascii=False).encode('utf-8'))
            return

        if self.path == '/api/flavors':
            flavors = load_json_file(FLAVORS_FILE, DEFAULT_FLAVORS)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(flavors, ensure_ascii=False).encode('utf-8'))
            return

        if self.path == '/api/drinks':
            drinks = load_json_file(DRINKS_FILE, DEFAULT_DRINKS)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(drinks, ensure_ascii=False).encode('utf-8'))
            return

        if self.path == '/api/customers/list':
            customers = load_json_file(CUSTOMERS_FILE, DEFAULT_CUSTOMERS)
            safe_cust = []
            for c in customers:
                safe_cust.append({
                    "phone": c.get("phone"),
                    "name": c.get("name"),
                    "email": c.get("email"),
                    "points": c.get("points", 0),
                    "createdAt": c.get("createdAt", "")
                })
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(safe_cust, ensure_ascii=False).encode('utf-8'))
            return

        if self.path == '/api/rewards':
            rewards = load_json_file(REWARDS_FILE, DEFAULT_REWARDS)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(rewards, ensure_ascii=False).encode('utf-8'))
            return

        super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            req_data = json.loads(body) if body else {}
        except Exception:
            req_data = {}

        # ORDERS
        if self.path == '/api/orders':
            orders = load_json_file(ORDERS_FILE, DEFAULT_ORDERS)
            orders.insert(0, req_data)
            save_json_file(ORDERS_FILE, orders)

            cust_phone = req_data.get('clientPhone', '').strip()
            total_spent = float(req_data.get('total', 0))
            pts_earned = int(total_spent)

            if cust_phone and pts_earned > 0:
                customers = load_json_file(CUSTOMERS_FILE, DEFAULT_CUSTOMERS)
                for c in customers:
                    if c.get('phone') == cust_phone:
                        c['points'] = c.get('points', 0) + pts_earned
                        save_json_file(CUSTOMERS_FILE, customers)
                        break

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "message": "Pedido de pizza recebido!"}).encode('utf-8'))
            return

        if self.path == '/api/orders/update-status':
            order_id = req_data.get('id')
            new_status = req_data.get('status')
            orders = load_json_file(ORDERS_FILE, DEFAULT_ORDERS)
            for o in orders:
                if o.get('id') == order_id:
                    o['status'] = new_status
                    break
            save_json_file(ORDERS_FILE, orders)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "orders": orders}).encode('utf-8'))
            return

        # COMBOS
        if self.path == '/api/combos':
            combos = load_json_file(COMBOS_FILE, DEFAULT_COMBOS)
            if req_data.get('id'):
                for c in combos:
                    if c.get('id') == req_data.get('id'):
                        c['name'] = req_data.get('name', c['name'])
                        c['price'] = float(req_data.get('price', c['price']))
                        break
            save_json_file(COMBOS_FILE, combos)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "combos": combos}).encode('utf-8'))
            return

        # FLAVORS
        if self.path == '/api/flavors':
            flavors = load_json_file(FLAVORS_FILE, DEFAULT_FLAVORS)
            if req_data.get('id'):
                updated = False
                for f in flavors:
                    if f.get('id') == req_data.get('id'):
                        f['name'] = req_data.get('name', f['name'])
                        f['desc'] = req_data.get('desc', f['desc'])
                        f['price'] = float(req_data.get('price', f['price']))
                        updated = True
                        break
                if not updated:
                    flavors.append(req_data)
            else:
                req_data['id'] = 'flav_' + str(int(os.urandom(4).hex(), 16))
                flavors.append(req_data)

            save_json_file(FLAVORS_FILE, flavors)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "flavors": flavors}).encode('utf-8'))
            return

        if self.path == '/api/flavors/delete':
            flav_id = req_data.get('id')
            flavors = load_json_file(FLAVORS_FILE, DEFAULT_FLAVORS)
            flavors = [f for f in flavors if f.get('id') != flav_id]
            save_json_file(FLAVORS_FILE, flavors)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "flavors": flavors}).encode('utf-8'))
            return

        # DRINKS
        if self.path == '/api/drinks':
            drinks = load_json_file(DRINKS_FILE, DEFAULT_DRINKS)
            if req_data.get('id'):
                updated = False
                for d in drinks:
                    if d.get('id') == req_data.get('id'):
                        d['name'] = req_data.get('name', d['name'])
                        d['price'] = float(req_data.get('price', d['price']))
                        updated = True
                        break
                if not updated:
                    drinks.append(req_data)
            else:
                req_data['id'] = 'drink_' + str(int(os.urandom(4).hex(), 16))
                drinks.append(req_data)

            save_json_file(DRINKS_FILE, drinks)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "drinks": drinks}).encode('utf-8'))
            return

        if self.path == '/api/drinks/delete':
            drink_id = req_data.get('id')
            drinks = load_json_file(DRINKS_FILE, DEFAULT_DRINKS)
            drinks = [d for d in drinks if d.get('id') != drink_id]
            save_json_file(DRINKS_FILE, drinks)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "drinks": drinks}).encode('utf-8'))
            return

        # CUSTOMERS
        if self.path == '/api/customers/register':
            phone = str(req_data.get('phone', '')).strip().replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
            name = req_data.get('name', '').strip()
            email = req_data.get('email', '').strip().lower()
            password = req_data.get('password', '').strip()

            if not phone or not name or not password:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": "Preencha Nome, WhatsApp e Senha."}).encode('utf-8'))
                return

            customers = load_json_file(CUSTOMERS_FILE, DEFAULT_CUSTOMERS)
            for c in customers:
                if c.get('phone') == phone:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "Este número de WhatsApp já possui conta."}).encode('utf-8'))
                    return

            new_c = {
                "phone": phone,
                "name": name,
                "email": email,
                "password": password,
                "points": 20,
                "createdAt": time.strftime("%Y-%m-%d")
            }
            customers.append(new_c)
            save_json_file(CUSTOMERS_FILE, customers)

            safe_info = { "phone": new_c["phone"], "name": new_c["name"], "email": new_c["email"], "points": new_c["points"] }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "customer": safe_info, "message": "Conta criada com sucesso! Você ganhou 20 pontos de bônus!"}).encode('utf-8'))
            return

        if self.path == '/api/customers/login':
            phone = str(req_data.get('phone', '')).strip().replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
            password = req_data.get('password', '').strip()

            customers = load_json_file(CUSTOMERS_FILE, DEFAULT_CUSTOMERS)
            found = None
            for c in customers:
                if c.get('phone') == phone and c.get('password') == password:
                    found = c
                    break

            if not found:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": "WhatsApp ou senha incorretos."}).encode('utf-8'))
                return

            safe_info = { "phone": found["phone"], "name": found["name"], "email": found["email"], "points": found["points"] }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "customer": safe_info}).encode('utf-8'))
            return

        if self.path == '/api/customers/update-points':
            phone = req_data.get('phone')
            new_points = int(req_data.get('points', 0))
            customers = load_json_file(CUSTOMERS_FILE, DEFAULT_CUSTOMERS)
            for c in customers:
                if c.get('phone') == phone:
                    c['points'] = new_points
                    break
            save_json_file(CUSTOMERS_FILE, customers)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
            return

        if self.path == '/api/customers/redeem':
            phone = req_data.get('phone')
            points_cost = int(req_data.get('points', 0))
            customers = load_json_file(CUSTOMERS_FILE, DEFAULT_CUSTOMERS)
            cust = None
            for c in customers:
                if c.get('phone') == phone:
                    cust = c
                    break

            if not cust or cust.get('points', 0) < points_cost:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": "Saldo de pontos insuficiente."}).encode('utf-8'))
                return

            cust['points'] -= points_cost
            save_json_file(CUSTOMERS_FILE, customers)
            safe_info = { "phone": cust["phone"], "name": cust["name"], "email": cust["email"], "points": cust["points"] }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "customer": safe_info}).encode('utf-8'))
            return

        # REWARDS
        if self.path == '/api/rewards':
            rewards = load_json_file(REWARDS_FILE, DEFAULT_REWARDS)
            if req_data.get('id'):
                updated = False
                for r in rewards:
                    if r.get('id') == req_data.get('id'):
                        r['name'] = req_data.get('name', r['name'])
                        r['points'] = int(req_data.get('points', r['points']))
                        r['value'] = float(req_data.get('value', r.get('value', 0)))
                        updated = True
                        break
                if not updated:
                    rewards.append(req_data)
            else:
                req_data['id'] = 'rew_' + str(int(os.urandom(4).hex(), 16))
                rewards.append(req_data)

            save_json_file(REWARDS_FILE, rewards)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "rewards": rewards}).encode('utf-8'))
            return

        if self.path == '/api/rewards/delete':
            rew_id = req_data.get('id')
            rewards = load_json_file(REWARDS_FILE, DEFAULT_REWARDS)
            rewards = [r for r in rewards if r.get('id') != rew_id]
            save_json_file(REWARDS_FILE, rewards)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "rewards": rewards}).encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()

if __name__ == '__main__':
    load_json_file(ORDERS_FILE, DEFAULT_ORDERS)
    load_json_file(COMBOS_FILE, DEFAULT_COMBOS)
    load_json_file(FLAVORS_FILE, DEFAULT_FLAVORS)
    load_json_file(DRINKS_FILE, DEFAULT_DRINKS)
    load_json_file(CUSTOMERS_FILE, DEFAULT_CUSTOMERS)
    load_json_file(REWARDS_FILE, DEFAULT_REWARDS)
    os.chdir(DATA_DIR)
    
    with socketserver.TCPServer(("", PORT), ReiDosReisRequestHandler) as httpd:
        print(f"Servidor Rei dos Reis Delivery rodando em http://localhost:{PORT}")
        httpd.serve_forever()
