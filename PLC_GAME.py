import pygame
from pygame.locals import *
import sys
import socket
import tkinter.messagebox as messagebox

maker = 'KEYENCE'
ip = '192.168.0.10'
port = 8501

io_input_type = "R"
io_input_no = "1000"
io_output_type = "R"
io_output_no = "5000"

def get_plc_comm_command(plc_input_list = []):
    command = ''
    send_data = ''

    if maker == 'KEYENCE':
        if len(plc_input_list) >= 16:
            for i in range(16):
                send_data += plc_input_list[15-i]

            send_data = int(send_data,2)      
            command = "WRS " + io_input_type + io_input_no + ".U 1 " + str(send_data) + "\r"
            command = command.encode("ascii")


        else:
            command = "RDS " + io_output_type + io_output_no + ".U 1\r"
            command = command.encode("ascii")

            

    return command

def get_plc_output(plc_output_list,response):

    if maker == 'KEYENCE':
        response = response.decode("UTF-8")
        response = bin(int(response))
        response = response.replace('0b','')
        plc_output = response.zfill(16)

        for i in range(16):
            plc_output_list[i] = plc_output[15-i:16-i]

    

class Sprite(pygame.sprite.Sprite):

    def __init__(self, name, x, y):
        pygame.sprite.Sprite.__init__(self)
 
        self.image = pygame.image.load(name).convert()
        colorkey = self.image.get_at((0,0))
        self.image.set_colorkey(colorkey, RLEACCEL)

        width  = self.image.get_width()
        height = self.image.get_height()
        self.rect = Rect(x, y, width, height)
 
    def check(self, pos):
        return self.rect.collidepoint(pos)
 
    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def change_img(self,name):
        self.image = pygame.image.load(name).convert()
        colorkey = self.image.get_at((0,0))
        self.image.set_colorkey(colorkey, RLEACCEL)

        
def main():
    pygame.init()
    pygame.display.set_caption("PLC GAME") 
    img_base = pygame.image.load("base.png")
    img_plc_input = pygame.image.load("io.png")
    screen = pygame.display.set_mode((img_base.get_width() + img_plc_input.get_width(),img_plc_input.get_height()))

    clock = pygame.time.Clock()
    
    is_left_key_down = False
    is_right_key_down = False
    is_change_work = False
    is_connecting = False
    try_connect = False
    sock = socket.socket(socket.AF_INET)
    sock.settimeout(3.0)

    
    
    plc_input_list = []
    plc_output_list = []
    for i in range(16):
        plc_input_list.append('0')
        plc_output_list.append('0')

    plc_input_list[9] = '1'
    

    dsw_no = 0
    work_no = 15

    dpl1_no = 0
    dpl2_no = 0

    bin_work_no = bin(work_no)
    bin_work_no = bin_work_no[2:]
    bin_work_no = bin_work_no.zfill(4)
    work_no_bit = []
    work_no_bit.append(bin_work_no[3:4])
    work_no_bit.append(bin_work_no[2:3])
    work_no_bit.append(bin_work_no[1:2])
    work_no_bit.append(bin_work_no[0:1])
        
    
    work_limit_left = 48
    work_limit_right = 329
    img_work = Sprite("work_15.png",work_limit_right,129)
    
    img_ss0_left = Sprite("selecter_left.png",8,332)
    img_ss0_right = Sprite("selecter_right.png",8,332)

    img_ss1_left = Sprite("selecter_left.png",58,332)
    img_ss1_right = Sprite("selecter_right.png",58,332)

    img_pb1 = Sprite("pb.png",108,332)
    img_pb2 = Sprite("pb.png",150,332)
    img_pb3 = Sprite("pb.png",192,332)
    img_pb4 = Sprite("pb.png",234,332)
    img_pb5 = Sprite("epb.png",285,325)



    pl_off = (100,100,100)
    pl_on = (0,255,0)
    pl_size = 10

    pl1_pos = (128,270)
    pl2_pos = (171,270)
    pl3_pos = (213,270)
    pl4_pos = (255,270)


    ls_font = pygame.font.Font("/Windows/Fonts/meiryo.ttc", 11)
    ls_text_list = []
    ls_text_list.append(ls_font.render("LS1", True, (0,0,0)))
    ls_text_list.append(ls_font.render("LS2", True, (0,0,0)))
    ls_text_list.append(ls_font.render("LS3", True, (0,0,0)))
    ls_text_list.append(ls_font.render("LS4", True, (0,0,0)))
    ls_text_list.append(ls_font.render("LS5", True, (0,0,0)))

    ls_rect_list = []
    ls_rect_list.append(Rect(348,186,50,12))
    ls_rect_list.append(Rect(65,186,50,12))
    ls_rect_list.append(Rect(65,169,50,12))
    ls_rect_list.append(Rect(65,152,50,12))
    ls_rect_list.append(Rect(65,135,50,12))

    dsw_font = pygame.font.Font("/Windows/Fonts/meiryo.ttc", 30)
    dsw_pos = (344,316)


    dpl_font = pygame.font.Font("/Windows/Fonts/meiryo.ttc", 42)
    dpl1_pos = (391,316)
    dpl2_pos = (432,316)

    font = pygame.font.Font("/Windows/Fonts/meiryo.ttc", 11)
    plc_font = pygame.font.Font("/Windows/Fonts/meiryo.ttc", 16)
    

    

    while True:
        if try_connect == True and is_connecting == False:
            try:
                sock.connect((ip,port))
                is_connecting = True
                try_connect = False
            except:
                is_connecting = False
                try_connect = False
                messagebox.showinfo("Info", "PLC接続 失敗")

        if is_connecting == True:
            try:
                command = get_plc_comm_command(plc_input_list)
                sock.send(command)
                response = sock.recv(4096)

                command = get_plc_comm_command()
                sock.send(command)
                response = sock.recv(4096)

                get_plc_output(plc_output_list,response)

                
                
            except:
                is_connecting = False
                messagebox.showinfo("Info", "コマンド送受信 失敗")

    
                
        
        screen.fill((255,255,255))
        screen.blit(img_base,(0,0))
        screen.blit(img_plc_input,(img_base.get_width(),0))

        pos_x_plc_input = img_base.get_width() + 129
        pos_y_plc_input = 18
        width_plc_input = 37

        input_x1 = pos_x_plc_input
        input_x2 = pos_x_plc_input + width_plc_input
            
        for i in range(16):
            if plc_input_list[i] == '1':
                input_color = (255,0,0)
            else:
                input_color = (0,0,0)
                
            if i != 9:
                input_y1 = pos_y_plc_input + i * 32
                input_y2 = input_y1
                    
                if plc_input_list[i] == '0':
                    input_y1 -= 4
                    input_y2 = input_y1
            else:
                input_y1 = pos_y_plc_input + i * 32 + 12
                input_y2 = input_y1
                    
                if plc_input_list[i] == '0':
                    input_y1 += 4
                    input_y2 = input_y1
            
            pygame.draw.line(screen, input_color, (input_x1,input_y1), (input_x2,input_y2), 3)
  
            y_text = pos_y_plc_input + i * 32 - 2
            text_input = io_input_type + str(int(io_input_no) + i)
            text = plc_font.render(text_input, True, input_color)
            screen.blit(text,(input_x2 + 60,y_text))


            if i <= 13:
                if plc_output_list[i] == '1':
                    output_color = (255,0,0)
                    output_text_color = (255,0,0)
                else:
                    output_color = (255,255,255)
                    output_text_color = (0,0,0)

                x_coil = img_base.get_width() + 479
                y_coil = 26 + i * 32
                pygame.draw.circle(screen,output_color,(x_coil,y_coil),12) 

                text_output = io_output_type + str(int(io_output_no) + i)
                text = plc_font.render(text_output, True, output_text_color)
                screen.blit(text,(input_x2 + 174,y_text))
        

        #------------------------------------------------------------------------------------------------
        #ワーク状態 変化 --------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------
        
        str_work_no = str(work_no).zfill(2)

        if is_change_work == True:
            img_work.change_img('work_' + str_work_no + '.png')
            is_change_work = False

        if is_left_key_down == True:
            if img_work.rect[0] >= work_limit_left:
                img_work.rect[0] -= 2
                
        elif is_right_key_down == True:
            if img_work.rect[0] <= work_limit_right:
                img_work.rect[0] += 2

        img_work.draw(screen)


        dsw_text = dsw_font.render(str(dsw_no), True, (255,255,255))
        screen.blit(dsw_text,dsw_pos)


        #------------------------------------------------------------------------------------------------
        #説明描画 ---------------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------

        pos_y = 5
        text_content = ' F1  : ボルト1'
        text = font.render(text_content, True, (0,0,0))
        screen.blit(text,(9,pos_y))

        pos_y += 15
        text_content = ' F2  : ボルト2'
        text = font.render(text_content, True, (0,0,0))
        screen.blit(text,(9,pos_y))

        pos_y += 15
        text_content = ' F3  : ボルト3'
        text = font.render(text_content, True, (0,0,0))
        screen.blit(text,(9,pos_y))

        pos_y += 15
        text_content = 'F11 : PLC 接続'
        text = font.render(text_content, True, (0,0,0))
        screen.blit(text,(10,pos_y))

        pos_y = 5
        text_content = '↑ : DSW 加算'
        text = font.render(text_content, True, (0,0,0))
        screen.blit(text,(120,pos_y))

        pos_y += 15
        text_content = '↓ : DSW 減算'
        text = font.render(text_content, True, (0,0,0))
        screen.blit(text,(120,pos_y))

        if is_connecting == True:
            text_content = 'PLC接続中'
            color = (255,0,0)
            
        else:
            text_content = 'PLC未接続'
            color = (255,255,255)
                
        text = plc_font.render(text_content, True, (0,0,0),color)   
        screen.blit(text,(390,5))

        
        #------------------------------------------------------------------------------------------------
        #Draw PLC INPUT ---------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------
        
        #LS1 - LS5
        for i in range(5):
            if plc_input_list[i] == '1':
                ls_color = (255,0,0)
            else:
                ls_color = (255,255,255)

            ls_rect = ls_rect_list[i]
            ls_text = ls_text_list[i]
        
            screen.fill((0,0,0),Rect(ls_rect[0]-2,ls_rect[1]-2,ls_rect[2]+4,ls_rect[3]+4))
            screen.fill(ls_color,ls_rect)
            screen.blit(ls_text,(ls_rect[0] + ls_rect[2]/3,ls_rect[1]-2))

        #PB1 - PB5
        img_pb1.draw(screen)
        img_pb2.draw(screen)
        img_pb3.draw(screen)
        img_pb4.draw(screen)
        img_pb5.draw(screen)

        
        #SS1
        if plc_input_list[10] == '1':
            img_ss1_right.draw(screen)
        else:
            img_ss1_left.draw(screen)

        #SS0
        if plc_input_list[11] == '1':
            img_ss0_right.draw(screen)
        else:
            img_ss0_left.draw(screen)
            
    
        #------------------------------------------------------------------------------------------------
        #Draw PLC OUTPUT --------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------
            
        #ｺﾝﾍﾞｱ左
        if plc_output_list[0] == '1':
            if img_work.rect[0] >= work_limit_left:
                img_work.rect[0] -= 2

        #ｺﾝﾍﾞｱ右
        if plc_output_list[1] == '1':
            if img_work.rect[0] <= work_limit_right:
                img_work.rect[0] += 2

        #PL1
        if plc_output_list[2] == '1':
            pygame.draw.circle(screen,(0,0,0),pl1_pos,pl_size+2) 
            pygame.draw.circle(screen,pl_on,pl1_pos,pl_size) 
        else:
            pygame.draw.circle(screen,(0,0,0),pl1_pos,pl_size+2) 
            pygame.draw.circle(screen,pl_off,pl1_pos,pl_size)

        #PL2
        if plc_output_list[3] == '1':
            pygame.draw.circle(screen,(0,0,0),pl2_pos,pl_size+2) 
            pygame.draw.circle(screen,pl_on,pl2_pos,pl_size) 
        else:
            pygame.draw.circle(screen,(0,0,0),pl2_pos,pl_size+2) 
            pygame.draw.circle(screen,pl_off,pl2_pos,pl_size)

        #PL3
        if plc_output_list[4] == '1':
            pygame.draw.circle(screen,(0,0,0),pl3_pos,pl_size+2) 
            pygame.draw.circle(screen,pl_on,pl3_pos,pl_size) 
        else:
            pygame.draw.circle(screen,(0,0,0),pl3_pos,pl_size+2) 
            pygame.draw.circle(screen,pl_off,pl3_pos,pl_size)

        #PL4
        if plc_output_list[5] == '1':
            pygame.draw.circle(screen,(0,0,0),pl4_pos,pl_size+2) 
            pygame.draw.circle(screen,pl_on,pl4_pos,pl_size) 
        else:
            pygame.draw.circle(screen,(0,0,0),pl4_pos,pl_size+2) 
            pygame.draw.circle(screen,pl_off,pl4_pos,pl_size) 


        #DPL1 - DPL2
        dpl1_no = int(plc_output_list[9] + plc_output_list[8] + plc_output_list[7] + plc_output_list[6],2)
        if dpl1_no <= 9:
            dpl1_text = dpl_font.render(str(dpl1_no), True, (255,0,0))
            screen.blit(dpl1_text,dpl1_pos)

        dpl2_no = int(plc_output_list[13] + plc_output_list[12] + plc_output_list[11] + plc_output_list[10],2)
        if dpl2_no <= 9:
            dpl2_text = dpl_font.render(str(dpl2_no), True, (255,0,0))
            screen.blit(dpl2_text,dpl2_pos)



        #------------------------------------------------------------------------------------------------
        #Check Mouse & Keyboard -------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------
            
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT: 
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN: 
                if event.key == K_LEFT:
                    is_left_key_down = True
                    
                elif event.key == K_RIGHT:
                   is_right_key_down = True

                elif event.key == K_UP:
                    dsw_no += 1
                    if dsw_no > 9:
                        dsw_no = 0
                    
                elif event.key == K_DOWN:
                    dsw_no -= 1
                    if dsw_no < 0:
                        dsw_no = 9

                elif event.key == K_F11:
                    try_connect = True

                if is_change_work == False:
                    if event.key == K_F1:
                        is_change_work = True
                        if work_no_bit[1] == '1':
                            work_no_bit[1] = '0'
                        else:
                            work_no_bit[1] = '1'

                    elif event.key == K_F2:
                        is_change_work = True
                        if work_no_bit[2] == '1':
                            work_no_bit[2] = '0'
                        else:
                            work_no_bit[2] = '1'

                    elif event.key == K_F3:
                        is_change_work = True
                        if work_no_bit[3] == '1':
                            work_no_bit[3] = '0'
                        else:
                            work_no_bit[3] = '1'

                
                        
                    
            elif event.type == KEYUP:
                is_change_work = False
                
                if event.key==K_LEFT:
                    is_left_key_down = False
                    
                elif event.key==K_RIGHT:
                    is_right_key_down = False


            elif event.type == pygame.MOUSEBUTTONDOWN:
                left_click, middle_click, right_click = pygame.mouse.get_pressed()
                x, y = pygame.mouse.get_pos()


                if left_click:
                    if img_pb1.check(event.pos) == True:
                        plc_input_list[5] = '1'
                        
                    elif img_pb2.check(event.pos) == True:
                        plc_input_list[6] = '1'
                        
                    elif img_pb3.check(event.pos) == True:
                        plc_input_list[7] = '1'
                        
                    elif img_pb4.check(event.pos) == True:
                        plc_input_list[8] = '1'

                    elif img_pb5.check(event.pos) == True:
                        if plc_input_list[9] == '1':
                            plc_input_list[9] = '0'
                        else:
                            plc_input_list[9] = '1'
                        
                    elif img_ss1_left.check(event.pos) == True:
                        if plc_input_list[10] == '1':
                            plc_input_list[10] = '0'
                        else:
                            plc_input_list[10] = '1'
                        
                    elif img_ss0_left.check(event.pos) == True:
                        if plc_input_list[11] == '1':
                            plc_input_list[11] = '0'
                        else:
                            plc_input_list[11] = '1'

                    

            elif event.type == pygame.MOUSEBUTTONUP:
                plc_input_list[5] = '0'   #PB1
                plc_input_list[6] = '0'   #PB2
                plc_input_list[7] = '0'   #PB3
                plc_input_list[8] = '0'   #PB4


        #------------------------------------------------------------------------------------------------
        #Set LS Status ----------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------

        work_no = int(work_no_bit[3] + work_no_bit[2] + work_no_bit[1] + work_no_bit[0],2)
 
        bin_work_no = bin(work_no)
        bin_work_no = bin_work_no[2:]
        bin_work_no = bin_work_no.zfill(4)
        work_bolt1 = bin_work_no[3:4]
        work_bolt2 = bin_work_no[2:3]
        work_bolt3 = bin_work_no[1:2]
        work_bolt4 = bin_work_no[0:1]
        #print(bin_work_no)

        if img_work.rect[0] >= work_limit_right:
            plc_input_list[0] = '1'
        else:
            plc_input_list[0] = '0'

            
        if img_work.rect[0] <= work_limit_left:
            plc_input_list[1] = '1'

            if work_bolt2 == '1':
                plc_input_list[2] = '1'
            else:
                plc_input_list[2] = '0'

            if work_bolt3 == '1':
                plc_input_list[3] = '1'
            else:
                plc_input_list[3] = '0'

            if work_bolt4 == '1':
                plc_input_list[4] = '1'
            else:
                plc_input_list[4] = '0'
                
        else:
            plc_input_list[1] = '0'
            plc_input_list[2] = '0'
            plc_input_list[3] = '0'
            plc_input_list[4] = '0'

        #------------------------------------------------------------------------------------------------
        #Set DSW Status ---------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------
            
        bin_dsw_no = bin(dsw_no)
        bin_dsw_no = bin_dsw_no[2:]
        bin_dsw_no = bin_dsw_no.zfill(4)
        plc_input_list[12] = bin_dsw_no[3:4]
        plc_input_list[13] = bin_dsw_no[2:3]
        plc_input_list[14] = bin_dsw_no[1:2]
        plc_input_list[15] = bin_dsw_no[0:1]
        


        #------------------------------------------------------------------------------------------------

        
        clock.tick(60)
        
                   
if __name__ == "__main__":
    main()
