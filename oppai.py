import sys
import os
import pyoppai


def parser(data):
    f = open("temp.osu","w+")
    f.write(data)
    f.close()
    path=os.path.abspath("temp.osu")
    return main(path)
    
def print_pp(acc, pp, aim_pp, speed_pp, acc_pp):
    print(
        "\n%.17g aim\n%.17g speed\n%.17g acc\n%.17g pp\nfor %.17g%%" %
            (aim_pp, speed_pp, acc_pp, pp, acc)
    )

def print_diff(stars, aim, speed):
    print(
        "\n%.17g stars\n%.17g aim stars\n%.17g speed stars" %
        (stars, aim, speed)
    )

def chk(ctx):
    err = pyoppai.err(ctx)

    if err:
        print(err)
        return err

def main(filepath):
    # if you need to multithread, create one ctx and buffer for each thread
    ctx = pyoppai.new_ctx()

    # parse beatmap ------------------------------------------------------------
    b = pyoppai.new_beatmap(ctx)

    BUFSIZE = 2000000 # should be big enough to hold the .osu file
    buf = pyoppai.new_buffer(BUFSIZE)

    pyoppai.parse(
        filepath,
        b,
        buf,
        BUFSIZE,

        # don't disable caching and use python script's folder for caching
        False,
        os.path.dirname(os.path.realpath(__file__))
    );

    chk(ctx)

    

    cs, od, ar, hp = pyoppai.stats(b)

   
    # diff calc ----------------------------------------------------------------
    dctx = pyoppai.new_d_calc_ctx(ctx)

    stars, aim, speed, _, _, _, _ = pyoppai.d_calc(dctx, b)
    s=chk(ctx)
    if type(s) == str:
        return s
    #print(stars+'stars')
    #print_diff(stars, aim, speed)

    # pp calc ------------------------------------------------------------------
    acc, pp, aim_pp, speed_pp, acc_pp = \
            pyoppai.pp_calc(ctx, aim, speed, b)

    #print_pp(acc, pp, aim_pp, speed_pp, acc_pp)

    # pp calc (with acc %) -----------------------------------------------------
    acc2, pp2, aim_pp2, speed_pp2, acc_pp2 = \
        pyoppai.pp_calc_acc(ctx, aim, speed, b, 95.0)

    
    #print_pp(acc, pp, aim_pp, speed_pp, acc_pp)
    # mods example -------------------------------------------------------------
    #print("\n----\nWith HDHR:")
    # mods are a bitmask, same as what the osu! api uses
    mods = pyoppai.hd | pyoppai.hr
    pyoppai.apply_mods(b, mods)
    # mods are map-changing, recompute diff
    stars, aim, speed, _, _, _, _ = pyoppai.d_calc(dctx, b)


    #print_diff(stars, aim, speed)

    acc3, pp3, aim_pp3, speed_pp3, acc_pp = \
            pyoppai.pp_calc(ctx, aim, speed, b, mods)

    

    #print_pp(acc, pp, aim_pp, speed_pp, acc_pp)
    #------------------------------
    x=[ pyoppai.artist(b),
                pyoppai.title(b),
                pyoppai.version(b),
                pyoppai.creator(b),
                cs,
                od,
                ar,
                hp,
                pyoppai.max_combo(b),
                stars,
                pp,
                acc,
                pp2,
                acc2,
                pp3,
                acc3]
    return x

