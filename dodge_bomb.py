import os
import sys
import random
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {  # 移動量辞書
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0)
}


os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRectまたは爆弾Rect
    戻り値：横方向，縦方向の画面内外判定結果
    画面内ならTrue,画面外ならFalse
    """
    yoko, tate = True, True  # 初期値：画面内
    if rct.left < 0 or WIDTH < rct.right:  # 横方向の画面外判定
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom: # 縦方向の画面外判定
        tate = False
    return yoko, tate  # 横方向，縦方向の画面内判定結果を返す
    

def gameover(screen: pg.Surface) -> None:  # ゲームオーバー画面
    """
    引数：ディスプレイ画面
    戻り値：画面を暗くする
            Game overの文字と両脇に泣いているこうかとんを表示する
            画面を更新した5秒後にゲームを終了する
    """
    blackout = pg.Surface((WIDTH,HEIGHT))
    blackout.fill((0, 0, 0))
    blackout.set_alpha(150)
    screen.blit(blackout,[0, 0])  # 背景を暗くする

    fonto = pg.font.Font(None, 80)
    go_txt = fonto.render("Game Over",True,(255, 255, 255))
    screen.blit(go_txt,[400,300])  # game overという文字を画面に表示する

    ckk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    screen.blit(ckk_img,[330,300])  # 左こうかとん
    screen.blit(ckk_img,[730,300])  # 右こうかとん

    pg.display.update()
    time.sleep(5)


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:  # 爆弾の拡大度、加速度のリストを返す
    """
    引数：なし
    戻り値：爆弾の拡大した画像を格納したリスト、1~10の加速度を格納したリスト
    画像を格納したリストはpg.Surface、加速度を格納したリストにはintの型で入っている
    """
    bb_accs = [a for a in range(1, 11)]
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    
    return bb_imgs, bb_accs


def get_kk_img(sum_mv: tuple[int, int]) -> pg.Surface:
    """
    引数：こうかとんの移動量タプル
    戻り値：移動量タプルに対応した画像Surface
    こうかとんの向きが動いた方向に向くようにする
    """
    kk_img = pg.image.load("fig/3.png")
    if sum_mv == (+5, 0):
        kk_img = pg.transform.flip(kk_img, True, False)
        kk_img = pg.transform.rotozoom(kk_img, 0, 0.9)
    elif sum_mv == (+5, +5):
        kk_img = pg.transform.flip(kk_img, True, False)
        kk_img = pg.transform.rotozoom(kk_img, -45, 0.9)
    elif sum_mv == (0, +5):
        kk_img = pg.transform.flip(kk_img, True, False)
        kk_img = pg.transform.rotozoom(kk_img, -90, 0.9)
    elif sum_mv == (+5, -5):
        kk_img = pg.transform.flip(kk_img, True, False)
        kk_img = pg.transform.rotozoom(kk_img, 45, 0.9)
    elif sum_mv == (0, +5):
        kk_img = pg.transform.flip(kk_img, True, False)
        kk_img = pg.transform.rotozoom(kk_img, 90, 0.9)
    elif sum_mv == (-5, 0):
        kk_img = pg.transform.rotozoom(kk_img, 0, 0.9)
    elif sum_mv == (-5, -5):
        kk_img = pg.transform.rotozoom(kk_img, -45, 0.9)
    elif sum_mv == (-5, +5):
        kk_img = pg.transform.rotozoom(kk_img, 45, 0.9)
    return kk_img


def calc_orientation(org: pg.Rect, dst: pg.Rect,current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    引数：爆弾の位置、こうかとんの位置、爆弾の方向ベクトル
    戻り値：爆弾からみたこうかとんの位置への爆弾の方向ベクトル
    """
    if (org[0] - dst[0] < 0):
        current_xy[0] *= -1
    elif(org[0] - dst[0] > 0):
        current_xy[0] *= +1

    if (org[1] - dst[1] < 0 ):
        current_xy[1] *= -1
    elif(org[1] - dst[1] > 0 ):
        current_xy[1] *= +1
    
    return current_xy[0],current_xy[1]


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg") 
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    bb_img = pg.Surface((20, 20)) 
    pg.draw.circle(bb_img, (255, 0, 0),(10, 10), 10)
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0,WIDTH)  # 横座標の乱数
    bb_rct.centery = random.randint(0,HEIGHT)  # 縦座標の乱数
    kk_rct.center = 300, 200
    vx, vy = +5, +5  # 爆弾の速度 
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct):  # こうかとんと爆弾の接触判定
            gameover(screen)
            return    
        
        screen.blit(bg_img, [0, 0]) 
        vx, vy = calc_orientation(bb_rct, kk_rct, [vx, vy])  # 爆弾追尾
        
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
            
        # if key_lst[pg.K_UP]:
        #     sum_mv[1] -= 5
        # if key_lst[pg.K_DOWN]:
        #     sum_mv[1] += 5
        # if key_lst[pg.K_LEFT]:
        #     sum_mv[0] -= 5
        # if key_lst[pg.K_RIGHT]:
        #     sum_mv[0] += 5
        

        bb_imgs, bb_accs = init_bb_imgs()  # 爆弾の拡大と加速度を取得
        avx = vx*bb_accs[min(tmr//500, 9)]  # 爆弾を加速
        bb_img = bb_imgs[min(tmr//500, 9)]  # 爆弾を拡大
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0],-sum_mv[1])  # 移動をなかったことにする
        kk_img = get_kk_img((0, 0)) 
        kk_img = get_kk_img(tuple(sum_mv))  # 飛ぶ方向に従ってこうかとん画像を切り替える
        screen.blit(kk_img, kk_rct)  # こうかとん描画
        bb_rct.move_ip(avx, vy)  # 爆弾移動
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1

        screen.blit(bb_img, bb_rct)  # 爆弾描画

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
