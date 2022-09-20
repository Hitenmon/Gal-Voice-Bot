#!/usr/bin/env python
# coding: utf-8
from scipy.io.wavfile import write
from torch import LongTensor, no_grad

from . import commons, utils
from .models import SynthesizerTrn
from .text import text_to_sequence
from .Translate import Translate


def get_text(text, hps, cleaned=False):
    if cleaned:
        text_norm = text_to_sequence(text, hps.symbols, [])
    else:
        text_norm = text_to_sequence(text, hps.symbols, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = LongTensor(text_norm)
    return text_norm

model_root = '../../TTSModels'
config_root = './plugins/gal_voice_bot/VITS/models'

model =[f.format(model_root) for f in [
            "{0}/ATRI.pth",
            "{0}/Yuzu.pth"]
        ]
config =[f.format(config_root) for f in [
            "{0}/ATRI/config.json",
            "{0}/Yuzu/config.json"]
        ]


hps_ms = [utils.get_hparams_from_file(c) for c in config]
net_g_ms = [SynthesizerTrn(
    len(h.symbols),
    h.data.filter_length // 2 + 1,
    h.train.segment_size // h.data.hop_length,
    n_speakers=h.data.n_speakers,
    **h.model) for h in hps_ms]
for m, n in zip(model, net_g_ms):
    utils.load_checkpoint(m, n)

def Trans(text="お兄ちゃん大好き", model=0, speaker_id=0, out_path='voice.wav'):
    text = Translate(text)
    stn_tst = get_text(text, hps_ms[model])
    # print_speakers(hps_ms.speakers)
    with no_grad():
        x_tst = stn_tst.unsqueeze(0)
        x_tst_lengths = LongTensor([stn_tst.size(0)])
        sid = LongTensor([speaker_id])
        audio = net_g_ms[model].infer(x_tst, x_tst_lengths, sid=sid, noise_scale=.667,
                                    noise_scale_w=0.8, length_scale=1)[0][0, 0].data.cpu().float().numpy()
    write(out_path, hps_ms[model].data.sampling_rate, audio)
    print('voice Successfully saved!')
