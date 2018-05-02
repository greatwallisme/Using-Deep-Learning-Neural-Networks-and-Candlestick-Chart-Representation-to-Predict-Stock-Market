import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import glob
import argparse
import os
from shutil import copyfile, move
from pathlib import Path

# https://github.com/matplotlib/mpl_finance
from mpl_finance import candlestick_ohlc


def isnan(value):
    try:
        import math
        return math.isnan(float(value))
    except:
        return False


def removeOutput(finput):
    if(Path(finput)).is_file():
        os.remove(finput)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--input',
                        help='a csv file of stock data', required=True)
    parser.add_argument('-l', '--seq_len',
                        help='num of sequence length', default=20)
    parser.add_argument('-lf', '--label_file',
                        help='a label_file')
    parser.add_argument('-d', '--dimension',
                        help='a dimension value')
    parser.add_argument('-t', '--dataset_type',
                        help='training or testing datasets')
    parser.add_argument('-m', '--mode',
                        help='mode of preprocessing data', required=True)
    args = parser.parse_args()
    if args.mode == 'ohlc2cs':
        ohlc2cs(args.input, args.seq_len, args.dataset_type)
    if args.mode == 'createLabel':
        createLabel(args.input, args.seq_len)
    if args.mode == 'img2dt':
        image2dataset(args.input, args.label_file)
    if args.mode == 'countImg':
        countImage(args.input)


def image2dataset(input, label_file):
    # python preprocess.py -m img2dt -i dataset/5/img -lf FTSE_label_5.txt
    label_dict = {}
    with open(label_file) as f:
        for line in f:
            (key, val) = line.split(',')
            # print("adding {} with key {}".format(val.rstrip(), key))
            label_dict[key] = val.rstrip()
    # print(label_dict)
    # print(list(label_dict.values())[list(label_dict.keys()).index('FTSE-80')])
    path = "{}/{}".format(os.getcwd(), input)
    print(path)
    # df = pd.DataFrame()
    # os.chdir("{}/{}/".format(os.getcwd(),input))
    # print(os.getcwd())

    # count_a = 0
    # count_b = 0
    # count_c = 0
    # count_d = 0
    # count_e = 0
    for filename in os.listdir(path):
        # print(filename)
        # print(os.getcwd())
        if filename is not '':
            for k, v in label_dict.items():
                splitname = filename.split("_")
                f, e = os.path.splitext(filename)
                print("[DEBUG] - {}".format(splitname))
                newname = "{}_{}".format(splitname[0], splitname[1])
                if newname == k:
                    # print("{} same with {} with v {}".format(filename, k, v))
                    new_name = "{}{}.png".format(v, f)

                    os.rename("{}/{}".format(path, filename),
                              "{}/{}".format(path, new_name))
                    break

    folders = ['1', '0']
    for folder in folders:
        if not os.path.exists("{}/classes/{}".format(path, folder)):
            os.makedirs("{}/classes/{}".format(path, folder))

    for filename in os.listdir(path):
        if filename is not '':
            # print(filename[:1])
            if filename[:1] == "1":
                move("{}/{}".format(path, filename),
                     "{}/classes/1/{}".format(path, filename))
            elif filename[:1] == "0":
                move("{}/{}".format(path, filename),
                     "{}/classes/0/{}".format(path, filename))


def createLabel(fname, seq_len):
    # python preprocess.py -m createLabel -l 20 -i stockdatas/EWT_training5.csv
    print("Creating label . . .")
    # remove existing label file
    filename = fname.split('/')
    # print("{} - {}".format(filename[0], filename[1][:-4]))
    removeOutput("{}_label_{}.txt".format(filename[1][:-4], seq_len))
    # removeOutput('perct_value_{}_{}'.format(filename[1][:-4], seq_len))
    # if os.path.exists("{}_label_{}.txt".format(filename[1][:-4],seq_len)):
    #     os.remove("{}_label_{}.txt".format(filename[1][:-4],seq_len))

    df = pd.read_csv(fname, parse_dates=True, index_col=0)
    df.fillna(0)

    df.reset_index(inplace=True)
    df['Date'] = df['Date'].map(mdates.date2num)
    for i in range(0, len(df)):
        c = df.ix[i:i + int(seq_len), :]
        starting = 0
        endvalue = 0
        label = ""
        # print("len(c) is {}".format(len(c)))
        # print(c)
        if len(c) == int(seq_len) + 1:
            for idx, val in enumerate(c['Close']):
                # print(idx,val)
                if idx == 0:
                    starting = float(val)
                if idx == len(c) - 1:
                    endvalue = float(val)
            if endvalue > starting:
                label = 1
            else:
                label = 0
            with open("{}_label_{}.txt".format(filename[1][:-4], seq_len), 'a') as the_file:
                the_file.write("{}-{},{}".format(filename[1][:-4], i, label))
                the_file.write("\n")
    print("Create label finished.")


def countImage(input):
    num_file = sum([len(files) for r, d, files in os.walk(input)])
    num_dir = sum([len(d) for r, d, files in os.walk(input)])
    print("num of files : {}\nnum of dir : {}".format(num_file, num_dir))


def ohlc2cs(fname, seq_len, dataset_type):
    # python preprocess.py -m ohlc2cs -l 20 -i stockdatas/EWT_testing.csv -t testing
    print("Converting olhc to candlestick")
    symbol = fname.split('_')[0]
    symbol = symbol.split('/')[1]
    print(symbol)
    path = "{}".format(os.getcwd())
    # print(path)
    if not os.path.exists("{}/dataset/{}/{}/{}".format(path, seq_len, symbol, dataset_type)):
        os.makedirs("{}/dataset/{}/{}/{}".format(path,
                                                 seq_len, symbol, dataset_type))

    df = pd.read_csv(fname, parse_dates=True, index_col=0)
    df.fillna(0)
    plt.style.use('dark_background')
    df.reset_index(inplace=True)
    df['Date'] = df['Date'].map(mdates.date2num)
    for i in range(0, len(df)):
        # normal length - begin
        # candlestick ohlc normal
        c = df.ix[i:i + int(seq_len) - 1, :]
        if len(c) == int(seq_len):
            # Date,Open,High,Low,Adj Close,Volume
            ohlc = zip(c['Date'], c['Open'], c['High'],
                       c['Low'], c['Close'], c['Volume'])
            my_dpi = 96
            fig = plt.figure(figsize=(48 / my_dpi, 48 / my_dpi), dpi=my_dpi)
            ax1 = plt.subplot2grid((1, 1), (0, 0))
            candlestick_ohlc(ax1, ohlc, width=0.4,
                             colorup='#77d879', colordown='#db3f3f')
            ax1.grid(False)
            ax1.set_xticklabels([])
            ax1.set_yticklabels([])
            ax1.xaxis.set_visible(False)
            ax1.yaxis.set_visible(False)
            ax1.axis('off')
            pngfile = 'dataset/{}/{}/{}/{}-{}_normal.png'.format(
                seq_len, symbol, dataset_type, fname[11:-4], i)
            fig.savefig(pngfile,  pad_inches=0, transparent=False)
            plt.close(fig)
        # volume plot
        if len(c) == int(seq_len):
            # Date,Open,High,Low,Adj Close,Volume
            ohlc = zip(c['Date'], c['Open'], c['High'],
                       c['Low'], c['Close'], c['Volume'])
            my_dpi = 96
            fig = plt.figure(figsize=(48 / my_dpi, 48 / my_dpi), dpi=my_dpi)
            ax1 = plt.subplot2grid((1, 1), (0, 0))

            dates = np.asarray(c['Date'])
            volume = np.asarray(c['Volume'])
            pos = c['Open']-c['Close'] < 0
            neg = c['Open']-c['Close'] > 0
            ax1.bar(dates[pos], volume[pos],
                    color='#77d879', width=1, align='center')
            ax1.bar(dates[neg], volume[neg],
                    color='#db3f3f', width=1, align='center')
            ax1.grid(False)
            ax1.set_xticklabels([])
            ax1.set_yticklabels([])
            ax1.xaxis.set_visible(False)
            ax1.yaxis.set_visible(False)
            ax1.axis('off')
            pngfile = 'dataset/{}/{}/{}/{}-{}_volume.png'.format(
                seq_len, symbol, dataset_type, fname[11:-4], i)
            fig.savefig(pngfile,  pad_inches=0, transparent=False)
            plt.close(fig)

        # ohlc+volume
        if len(c) == int(seq_len):
            # Date,Open,High,Low,Adj Close,Volume
            ohlc = zip(c['Date'], c['Open'], c['High'],
                       c['Low'], c['Close'], c['Volume'])
            my_dpi = 96
            fig = plt.figure(figsize=(48 / my_dpi, 48 / my_dpi), dpi=my_dpi)
            ax1 = fig.add_subplot(1, 1, 1)
            candlestick_ohlc(ax1, ohlc, width=1,
                             colorup='#77d879', colordown='#db3f3f')
            ax1.grid(False)
            ax1.set_xticklabels([])
            ax1.set_yticklabels([])
            ax1.xaxis.set_visible(False)
            ax1.yaxis.set_visible(False)
            ax1.axis('off')
            pad = 0.25
            yl = ax1.get_ylim()
            ax1.set_ylim(yl[0]-(yl[1]-yl[0])*pad, yl[1])
            # create the second axis for the volume bar-plot
            ax2 = ax1.twinx()
            ax2.set_position(matplotlib.transforms.Bbox(
                [[0.125, 0.1], [0.9, 0.32]]))
            dates = np.asarray(c['Date'])
            volume = np.asarray(c['Volume'])
            pos = c['Open']-c['Close'] < 0
            neg = c['Open']-c['Close'] > 0
            ax2.bar(dates[pos], volume[pos],
                    color='#77d879', width=1, align='center')
            ax2.bar(dates[neg], volume[neg],
                    color='#db3f3f', width=1, align='center')
            ax2.grid(False)
            ax2.set_xticklabels([])
            ax2.set_yticklabels([])
            ax2.xaxis.set_visible(False)
            ax2.yaxis.set_visible(False)
            ax2.axis('off')
            pngfile = 'dataset/{}/{}/{}/{}-{}_combination.png'.format(
                seq_len, symbol, dataset_type, fname[11:-4], i)
            fig.savefig(pngfile,  pad_inches=0, transparent=False)
            plt.close(fig)
        # normal length - end

        # length minus 1 - begin
        c1 = df.ix[i:i + int(seq_len) - 2, :]
        if len(c1) == int(seq_len)-1:
            # Date,Open,High,Low,Adj Close,Volume
            ohlc = zip(c1['Date'], c1['Open'], c1['High'],
                       c1['Low'], c1['Close'], c1['Volume'])
            my_dpi = 96
            fig = plt.figure(figsize=(48 / my_dpi, 48 / my_dpi), dpi=my_dpi)
            ax1 = plt.subplot2grid((1, 1), (0, 0))
            candlestick_ohlc(ax1, ohlc, width=0.4,
                             colorup='#77d879', colordown='#db3f3f')
            ax1.grid(False)
            ax1.set_xticklabels([])
            ax1.set_yticklabels([])
            ax1.xaxis.set_visible(False)
            ax1.yaxis.set_visible(False)
            ax1.axis('off')
            pngfile = 'dataset/{}/{}/{}/{}-{}_normal_minone.png'.format(
                seq_len, symbol, dataset_type, fname[11:-4], i)
            fig.savefig(pngfile,  pad_inches=0, transparent=False)
            plt.close(fig)
        # volume plot
        if len(c1) == int(seq_len)-1:
            # Date,Open,High,Low,Adj Close,Volume
            ohlc = zip(c1['Date'], c1['Open'], c1['High'],
                       c1['Low'], c1['Close'], c1['Volume'])
            my_dpi = 96
            fig = plt.figure(figsize=(48 / my_dpi, 48 / my_dpi), dpi=my_dpi)
            ax1 = plt.subplot2grid((1, 1), (0, 0))

            dates = np.asarray(c1['Date'])
            volume = np.asarray(c1['Volume'])
            pos = c1['Open']-c1['Close'] < 0
            neg = c1['Open']-c1['Close'] > 0
            ax1.bar(dates[pos], volume[pos],
                    color='#77d879', width=1, align='center')
            ax1.bar(dates[neg], volume[neg],
                    color='#db3f3f', width=1, align='center')
            ax1.grid(False)
            ax1.set_xticklabels([])
            ax1.set_yticklabels([])
            ax1.xaxis.set_visible(False)
            ax1.yaxis.set_visible(False)
            ax1.axis('off')
            pngfile = 'dataset/{}/{}/{}/{}-{}_volume_minone.png'.format(
                seq_len, symbol, dataset_type, fname[11:-4], i)
            fig.savefig(pngfile,  pad_inches=0, transparent=False)
            plt.close(fig)

        # ohlc+volume
        if len(c1) == int(seq_len)-1:
            # Date,Open,High,Low,Adj Close,Volume
            ohlc = zip(c1['Date'], c1['Open'], c1['High'],
                       c1['Low'], c1['Close'], c1['Volume'])
            my_dpi = 96
            fig = plt.figure(figsize=(48 / my_dpi, 48 / my_dpi), dpi=my_dpi)
            ax1 = fig.add_subplot(1, 1, 1)
            candlestick_ohlc(ax1, ohlc, width=1,
                             colorup='#77d879', colordown='#db3f3f')
            ax1.grid(False)
            ax1.set_xticklabels([])
            ax1.set_yticklabels([])
            ax1.xaxis.set_visible(False)
            ax1.yaxis.set_visible(False)
            ax1.axis('off')
            pad = 0.25
            yl = ax1.get_ylim()
            ax1.set_ylim(yl[0]-(yl[1]-yl[0])*pad, yl[1])
            # create the second axis for the volume bar-plot
            ax2 = ax1.twinx()
            ax2.set_position(matplotlib.transforms.Bbox(
                [[0.125, 0.1], [0.9, 0.32]]))
            dates = np.asarray(c1['Date'])
            volume = np.asarray(c1['Volume'])
            pos = c1['Open']-c1['Close'] < 0
            neg = c1['Open']-c1['Close'] > 0
            ax2.bar(dates[pos], volume[pos],
                    color='#77d879', width=1, align='center')
            ax2.bar(dates[neg], volume[neg],
                    color='#db3f3f', width=1, align='center')
            ax2.grid(False)
            ax2.set_xticklabels([])
            ax2.set_yticklabels([])
            ax2.xaxis.set_visible(False)
            ax2.yaxis.set_visible(False)
            ax2.axis('off')
            pngfile = 'dataset/{}/{}/{}/{}-{}_combination_minone.png'.format(
                seq_len, symbol, dataset_type, fname[11:-4], i)
            fig.savefig(pngfile,  pad_inches=0, transparent=False)
            plt.close(fig)
        # length minus 1 - end

        # length plus 1 - begin
        c2 = df.ix[i:i + int(seq_len), :]
        if len(c2) == int(seq_len):
            # Date,Open,High,Low,Adj Close,Volume
            ohlc = zip(c2['Date'], c2['Open'], c2['High'],
                       c2['Low'], c2['Close'], c2['Volume'])
            my_dpi = 96
            fig = plt.figure(figsize=(48 / my_dpi, 48 / my_dpi), dpi=my_dpi)
            ax1 = plt.subplot2grid((1, 1), (0, 0))
            candlestick_ohlc(ax1, ohlc, width=0.4,
                             colorup='#77d879', colordown='#db3f3f')
            ax1.grid(False)
            ax1.set_xticklabels([])
            ax1.set_yticklabels([])
            ax1.xaxis.set_visible(False)
            ax1.yaxis.set_visible(False)
            ax1.axis('off')
            pngfile = 'dataset/{}/{}/{}/{}-{}_normal_minone.png'.format(
                seq_len, symbol, dataset_type, fname[11:-4], i)
            fig.savefig(pngfile,  pad_inches=0, transparent=False)
            plt.close(fig)
        # volume plot
        if len(c2) == int(seq_len):
            # Date,Open,High,Low,Adj Close,Volume
            ohlc = zip(c2['Date'], c2['Open'], c2['High'],
                       c2['Low'], c2['Close'], c2['Volume'])
            my_dpi = 96
            fig = plt.figure(figsize=(48 / my_dpi, 48 / my_dpi), dpi=my_dpi)
            ax1 = plt.subplot2grid((1, 1), (0, 0))

            dates = np.asarray(c2['Date'])
            volume = np.asarray(c2['Volume'])
            pos = c2['Open']-c2['Close'] < 0
            neg = c2['Open']-c2['Close'] > 0
            ax1.bar(dates[pos], volume[pos],
                    color='#77d879', width=1, align='center')
            ax1.bar(dates[neg], volume[neg],
                    color='#db3f3f', width=1, align='center')
            ax1.grid(False)
            ax1.set_xticklabels([])
            ax1.set_yticklabels([])
            ax1.xaxis.set_visible(False)
            ax1.yaxis.set_visible(False)
            ax1.axis('off')
            pngfile = 'dataset/{}/{}/{}/{}-{}_volume_minone.png'.format(
                seq_len, symbol, dataset_type, fname[11:-4], i)
            fig.savefig(pngfile,  pad_inches=0, transparent=False)
            plt.close(fig)

        # ohlc+volume
        if len(c2) == int(seq_len):
            # Date,Open,High,Low,Adj Close,Volume
            ohlc = zip(c2['Date'], c2['Open'], c2['High'],
                       c2['Low'], c2['Close'], c2['Volume'])
            my_dpi = 96
            fig = plt.figure(figsize=(48 / my_dpi, 48 / my_dpi), dpi=my_dpi)
            ax1 = fig.add_subplot(1, 1, 1)
            candlestick_ohlc(ax1, ohlc, width=1,
                             colorup='#77d879', colordown='#db3f3f')
            ax1.grid(False)
            ax1.set_xticklabels([])
            ax1.set_yticklabels([])
            ax1.xaxis.set_visible(False)
            ax1.yaxis.set_visible(False)
            ax1.axis('off')
            pad = 0.25
            yl = ax1.get_ylim()
            ax1.set_ylim(yl[0]-(yl[1]-yl[0])*pad, yl[1])
            # create the second axis for the volume bar-plot
            ax2 = ax1.twinx()
            ax2.set_position(matplotlib.transforms.Bbox(
                [[0.125, 0.1], [0.9, 0.32]]))
            dates = np.asarray(c2['Date'])
            volume = np.asarray(c2['Volume'])
            pos = c2['Open']-c2['Close'] < 0
            neg = c2['Open']-c2['Close'] > 0
            ax2.bar(dates[pos], volume[pos],
                    color='#77d879', width=1, align='center')
            ax2.bar(dates[neg], volume[neg],
                    color='#db3f3f', width=1, align='center')
            ax2.grid(False)
            ax2.set_xticklabels([])
            ax2.set_yticklabels([])
            ax2.xaxis.set_visible(False)
            ax2.yaxis.set_visible(False)
            ax2.axis('off')
            pngfile = 'dataset/{}/{}/{}/{}-{}_combination_minone.png'.format(
                seq_len, symbol, dataset_type, fname[11:-4], i)
            fig.savefig(pngfile,  pad_inches=0, transparent=False)
            plt.close(fig)
        # length plus 1 - end
    print("Converting olhc to candlestik finished.")



    # imagemagic script to resize img
    #  find . -maxdepth 4 -iname "*.png" | xargs -L1 -I{} convert -flatten +matte -adaptive-resize 200x200! "{}" "{}"
    # R Script convert html to img
    # library(webshot)
    # html_files <- list.files(pattern = ".html$", recursive = TRUE)
    # for(i in html_files){
    #   webshot(i, sprintf("%s", paste(i, "png", sep=".")),delay = 0.5)
    #   #print(sprintf("%s", paste(i, "png", sep=".")))
    #   print("done")
    # }
if __name__ == '__main__':
    main()
