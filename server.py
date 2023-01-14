import asyncio
import websockets
import json
clients = [] # store all connected cleints
players = []
click = []
land = [[0 for i in range(5)] for j in range(5)]

# handler for socket message activities
async def handler(websocket, path):
    # print(path) # path is not used currently
    if websocket not in clients:
        clients.append(websocket) # append new cleint to the array
    async for message in websocket:
        global players
        global land
        global click
        msg = message.split('###')
        print(msg,'received from client') # print to console
        # 進入homepage
        if msg[0] == "number":
            if len(players)==2:
                await websocket.send("已額滿")
            else:
                await broadcast(str(len(players)))
        # 玩家點擊進入遊戲的按鈕
        elif msg[0]=="play":
            if len(players)==2:
                click.append(websocket)
                await websocket.send("已額滿")
            else:
                players.append(websocket)
                await broadcast_click(str(len(players))+"###is preparing")
        # 搶土地
        elif msg[0] == "land":
            msg[1] = str(msg[1])
            row = int(msg[1][1]) # 搶到的地
            column = int(msg[1][0]) # 搶到的地
            # 玩家1(palyer_blue) ++ 
            if websocket == players[0]: 
                land[row][column] += 1
                r = msg[1][1]
                c = msg[1][0]
                point = str(land[row][column])
                await color(r+"###"+c+"###"+point+"###"+"occupied")
            # 玩家2(palyer_red) --
            else: 
                land[row][column] -= 1
                r = msg[1][1]
                c = msg[1][0]
                point = str(land[row][column])
                await color(r+"###"+c+"###"+point+"###"+"occupied")
        # 時間到
        elif msg[0] == "stop":
            palyer_blue = 0
            palyer_red = 0
            match_results = "tie" # 比賽結果
            for r in range(len(land)):
                for c in range(len(land)):
                    if land[r][c] > 0:
                        palyer_blue += 1
                    elif land[r][c] < 0:
                        palyer_red += 1
            if palyer_blue > palyer_red:
                match_results = "palyer_blue"
            elif palyer_blue < palyer_red:
                match_results = "palyer_red"
            await color(str(palyer_blue)+"###"+str(palyer_red)+"###"+match_results+"###"+"is winner")
        elif msg[0] == "out":
            players = []
            land = [[0 for i in range(5)] for j in range(5)]
            await broadcast_click(str(len(players))+"###prepare")
        
        # elif msg[0] == "whoareyou":
        #     if websocket == players[0]:
        #         await websocket.send("blue")
        #         # await broadcast_click("blue"+"###whoareyou")
        #     else: 
        #         await websocket.send("red")
        #         # await broadcast_click("red"+"###whoareyou")

async def broadcast_click(msg):
    m = msg.split("###")
    await broadcast(m[0])
    print(m,'show_number') # 玩家點擊進入遊戲
    for websock in click:
        try:
            await websock.send(msg) # send message to each client
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected. Do cleanup ")
            clients.remove(websock)

async def broadcast(msg):
    m = msg.split("###")
    print(m,'show_number') # 玩家進入homepage
    for websock in clients:
        if websock not in click:
            try:
                await websock.send(msg) # send message to each client
            except websockets.exceptions.ConnectionClosed:
                print("Client disconnected. Do cleanup")
                clients.remove(websock)
        
async def color(msg):
    m = msg.split("###")
    print(m,'color')
    for websock in players:
        try:
            await websock.send(msg) # send message to each client
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected. Do cleanup ")
            clients.remove(websock)

#starts the service and run forever
loop = asyncio.new_event_loop() #get an event loop
asyncio.set_event_loop(loop) #set the event loop to asyncio
loop.run_until_complete(
    # 10.99.1.149
    websockets.serve(handler,'10.99.1.149', 4545) #setup the websocket service and handler
    ) #hook to localhost:4545
loop.run_forever() #keep it running