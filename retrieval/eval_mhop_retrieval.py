"""
python eval_mhop_retrieval.py /private/home/xwhan/data/hotpot/hotpot_qas_val.json index/abstracts_roberta.npy index/hotpotQA_corpus_dict.json logs/08-16-2020/roberta_momentum_freeze_k-seed16-bsz150-fp16True-lr1e-05-decay0.0-warm0-valbsz3000-m0.999-k76800/checkpoint_q_best.pt --batch-size 50 --beam-size-1 20 --beam-size-2 5 --topk 20 --shared-encoder --model-name roberta-base --gpu --hnsw --save-path dense_val_b20_5_k20_hnsw_best.json

python eval_mhop_retrieval.py /private/home/xwhan/data/hotpot/hotpot_qas_val.json index/abstracts_roberta.npy index/hotpotQA_corpus_dict.json logs/08-16-2020/roberta_momentum_freeze_k-seed16-bsz150-fp16True-lr1e-05-decay0.0-warm0-valbsz3000-m0.999-k76800/checkpoint_q_best.pt --batch-size 50 --beam-size-1 20 --beam-size-2 20 --topk 20 --shared-encoder --model-name roberta-base --gpu --only-eval-ans

python eval_mhop_retrieval.py /private/home/xwhan/data/hotpot/hotpot_qas_val.json index/abstracts_roberta_no_linked_neg.npy index/hotpotQA_corpus_dict.json logs/09-12-2020/roberta_momentm_no_linked-seed16-bsz150-fp16True-lr1e-05-decay0.0-warm0-valbsz3000-m0.999-k76800-t1.0/checkpoint_q_best.pt --batch-size 50 --beam-size-1 20 --beam-size-2 20 --topk 20 --shared-encoder --model-name roberta-base --gpu


# unified 
python eval_mhop_retrieval.py /private/home/xwhan/data/hotpot/hotpot_qas_val.json index/merged_all.npy index/merged_all_id2doc.json logs/07-24-2020/unified_continue-seed16-bsz150-fp16True-lr1e-05-decay0.0/checkpoint_best.pt --shared-encoder --model-name bert-base-uncased --unified --batch-size 50  --beam-size-1 20 --beam-size-2 20 --topk 20 --only-eval-ans

python eval_mhop_retrieval.py /private/home/xwhan/data/hotpot/hotpot_qas_val.json index/merged_all_retrained_no_period.npy index/merged_all_id2doc.json logs/09-15-2020/unified_bert_no_period-seed16-bsz128-fp16True-lr2e-05-decay0.0-adamTrue/checkpoint_best.pt --shared-encoder --model-name bert-base-uncased --unified --batch-size 50  --beam-size-1 20 --beam-size-2 20 --topk 20 --only-eval-ans

# evaluate on the merged corpus
python eval_mhop_retrieval.py /private/home/xwhan/data/hotpot/hotpot_qas_val.json index/merged_all_roberta.npy index/merged_all_id2doc.json logs/08-16-2020/roberta_momentum_freeze_k-seed16-bsz150-fp16True-lr1e-05-decay0.0-warm0-valbsz3000-m0.999-k76800/checkpoint_q_best.pt --shared-encoder --model-name roberta-base --batch-size 200  --beam-size-1 5 --beam-size-2 5 --topk 5 --only-eval-ans



# BERT baseline
python eval_mhop_retrieval.py /private/home/xwhan/data/hotpot/hotpot_qas_val.json index/abstracts_baseline.npy index/hotpotQA_corpus_dict.json logs/07-31-2020/baseline-seed16-bsz150-fp16True-lr1e-05-decay0.0/checkpoint_best.pt --shared-encoder --model-name bert-base-uncased --batch-size 200  --beam-size-1 5 --beam-size-2 5 --topk 5 --only-eval-ans --gpu

# BERT-base evaluate on the merged corpus
python eval_mhop_retrieval.py /private/home/xwhan/data/hotpot/hotpot_qas_val.json index/merged_all_hotpot_only.npy index/merged_all_id2doc.json logs/07-31-2020/baseline-seed16-bsz150-fp16True-lr1e-05-decay0.0/checkpoint_best.pt --shared-encoder --model-name bert-base-uncased --batch-size 1000  --beam-size-1 1 --beam-size-2 1 --topk 1 --only-eval-ans --gpu

python eval_mhop_retrieval.py /private/home/xwhan/data/hotpot/hotpot_qas_val.json index/abstracts_baseline.npy index/hotpotQA_corpus_dict.json logs/07-31-2020/baseline-seed16-bsz150-fp16True-lr1e-05-decay0.0/checkpoint_best.pt --shared-encoder --model-name bert-base-uncased --batch-size 1000  --beam-size-1 1 --beam-size-2 1 --topk 1 --gpu --only-eval-ans


# ablation no memory bank update
python eval_mhop_retrieval.py /private/home/xwhan/data/hotpot/hotpot_qas_val.json index/abstracts_roberta.npy index/hotpotQA_corpus_dict.json logs/08-08-2020/roberta_v0_fixed-seed16-bsz150-fp16True-lr2e-05-decay0.0-warm0.1-valbsz3000-sharedTrue-multi1-schemenone/checkpoint_best.pt --batch-size 1000 --beam-size-1 1 --beam-size-2 1 --topk 1 --shared-encoder --model-name roberta-base --gpu --only-eval-ans


# single-hop baseline for hotpotQA
python eval_mhop_retrieval.py /private/home/xwhan/data/hotpot/hotpot_qas_val.json index/abstracts_single.npy index/hotpotQA_corpus_dict.json logs/09-10-2020/hotpot_single-seed16-bsz256-fp16True-lr2e-05-decay0.0-warm0.1-roberta-base/checkpoint_best.pt --batch-size 50 --beam-size-1 20 --beam-size-2 20 --topk 20 --shared-encoder --model-name roberta-base --gpu --only-eval-ans


"""
import argparse
import collections
import json
import logging
from os import path
import time

import faiss
import numpy as np
import torch
from tqdm import tqdm
from transformers import AutoConfig, AutoTokenizer

from models.mhop_retriever import MhopRetriever, RobertaRetriever
from models.unified_retriever import UnifiedRetriever
from utils.basic_tokenizer import SimpleTokenizer
from utils.utils import (load_saved, move_to_cuda, para_has_answer)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if (logger.hasHandlers()):
    logger.handlers.clear()
console = logging.StreamHandler()
logger.addHandler(console)

def convert_hnsw_query(query_vectors):
    aux_dim = np.zeros(len(query_vectors), dtype='float32')
    query_nhsw_vectors = np.hstack((query_vectors, aux_dim.reshape(-1, 1)))
    return query_nhsw_vectors

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('raw_data', type=str, default=None)
    parser.add_argument('indexpath', type=str, default=None)
    parser.add_argument('corpus_dict', type=str, default=None)
    parser.add_argument('model_path', type=str, default=None)
    parser.add_argument('--topk', type=int, default=2, help="topk paths")
    parser.add_argument('--num-workers', type=int, default=10)
    parser.add_argument('--max-q-len', type=int, default=70)
    parser.add_argument('--max-c-len', type=int, default=300)
    parser.add_argument('--max-q-sp-len', type=int, default=350)
    parser.add_argument('--batch-size', type=int, default=100)
    parser.add_argument('--beam-size-1', type=int, default=5)
    parser.add_argument('--beam-size-2', type=int, default=5)
    parser.add_argument('--model-name', type=str, default='bert-base-uncased')
    parser.add_argument('--gpu', action="store_true")
    parser.add_argument('--save-index', action="store_true")
    parser.add_argument('--only-eval-ans', action="store_true")
    parser.add_argument('--shared-encoder', action="store_true")
    parser.add_argument("--save-path", type=str, default="")
    parser.add_argument("--stop-drop", default=0, type=float)
    parser.add_argument("--unified", action="store_true")
    parser.add_argument('--hnsw', action="store_true")
    args = parser.parse_args()
    
    logger.info("Loading data...")
    ds_items = [json.loads(_) for _ in open(args.raw_data).readlines()]

    # filter
    if args.only_eval_ans:
        ds_items = [_ for _ in ds_items if _["answer"][0] not in ["yes", "no"]]

    logger.info("Building index...")
    d = 768
    xb = np.load(args.indexpath).astype('float32')
    print(xb.shape)

    if args.hnsw:
        if path.exists("index/wiki_index_hnsw_roberta"):
            index = faiss.read_index("index/wiki_index_hnsw_roberta")
        else:
            index = faiss.IndexHNSWFlat(d + 1, 512)
            index.hnsw.efSearch = 128
            index.hnsw.efConstruction = 200
            phi = 0
            for i, vector in enumerate(xb):
                norms = (vector ** 2).sum()
                phi = max(phi, norms)
            logger.info('HNSWF DotProduct -> L2 space phi={}'.format(phi))

            data = xb
            buffer_size = 50000
            n = len(data)
            print(n)
            for i in tqdm(range(0, n, buffer_size)):
                vectors = [np.reshape(t, (1, -1)) for t in data[i:i + buffer_size]]
                norms = [(doc_vector ** 2).sum() for doc_vector in vectors]
                aux_dims = [np.sqrt(phi - norm) for norm in norms]
                hnsw_vectors = [np.hstack((doc_vector, aux_dims[idx].reshape(-1, 1))) for idx, doc_vector in enumerate(vectors)]
                hnsw_vectors = np.concatenate(hnsw_vectors, axis=0)
                index.add(hnsw_vectors)
    else:
        index = faiss.IndexFlatIP(d)
        index.add(xb)
        if args.gpu:
            res = faiss.StandardGpuResources()
            index = faiss.index_cpu_to_gpu(res, 1, index)

    if args.save_index:
        faiss.write_index(index, "index/wiki_index_hnsw_roberta")
    
    logger.info(f"Loading corpus...")
    id2doc = json.load(open(args.corpus_dict))
    if isinstance(id2doc["0"], list):
        id2doc = {k: {"title":v[0], "text": v[1]} for k, v in id2doc.items()}
    # title2text = {v[0]:v[1] for v in id2doc.values()}
    logger.info(f"Corpus size {len(id2doc)}")
    
    logger.info("Loading trained model...")
    bert_config = AutoConfig.from_pretrained(args.model_name)
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    if args.unified:
        model = UnifiedRetriever(bert_config, args)
    elif "roberta" in args.model_name:
        model = RobertaRetriever(bert_config, args)
    else:
        model = MhopRetriever(bert_config, args)
    model = load_saved(model, args.model_path, exact=False)
    simple_tokenizer = SimpleTokenizer()

    cuda = torch.device('cuda')
    model.to(cuda)
    from apex import amp
    model = amp.initialize(model, opt_level='O1')
    model.eval()

    logger.info("Encoding questions and searching")
    questions = [_["question"][:-1] if _["question"].endswith("?") else _["question"] for _ in ds_items]
    metrics = []
    retrieval_outputs = []
    for b_start in tqdm(range(0, len(questions), args.batch_size)):
        with torch.no_grad():
            batch_q = questions[b_start:b_start + args.batch_size]
            batch_ann = ds_items[b_start:b_start + args.batch_size]
            bsize = len(batch_q)

            batch_q_encodes = tokenizer.batch_encode_plus(batch_q, max_length=args.max_q_len, pad_to_max_length=True, return_tensors="pt")
            batch_q_encodes = move_to_cuda(dict(batch_q_encodes))
            q_embeds = model.encode_q(batch_q_encodes["input_ids"], batch_q_encodes["attention_mask"], batch_q_encodes.get("token_type_ids", None))

            q_embeds_numpy = q_embeds.cpu().contiguous().numpy()
            if args.hnsw:
                q_embeds_numpy = convert_hnsw_query(q_embeds_numpy)
            D, I = index.search(q_embeds_numpy, args.beam_size_1)

            # 2hop search
            query_pairs = []
            for b_idx in range(bsize):
                for _, doc_id in enumerate(I[b_idx]):
                    doc = id2doc[str(doc_id)]["text"]
                    if "roberta" in  args.model_name and doc.strip() == "":
                        # doc = "fadeaxsaa" * 100
                        doc = id2doc[str(doc_id)]["title"]
                        D[b_idx][_] = float("-inf")
                    query_pairs.append((batch_q[b_idx], doc))

            batch_q_sp_encodes = tokenizer.batch_encode_plus(query_pairs, max_length=args.max_q_sp_len, pad_to_max_length=True, return_tensors="pt")
            batch_q_sp_encodes = move_to_cuda(dict(batch_q_sp_encodes))
            s1 = time.time()
            q_sp_embeds = model.encode_q(batch_q_sp_encodes["input_ids"], batch_q_sp_encodes["attention_mask"], batch_q_sp_encodes.get("token_type_ids", None))
            # print("Encoding time:", time.time() - s1)

            
            q_sp_embeds = q_sp_embeds.contiguous().cpu().numpy()
            s2 = time.time()
            if args.hnsw:
                q_sp_embeds = convert_hnsw_query(q_sp_embeds)
            # search_start = time.time()
            D_, I_ = index.search(q_sp_embeds, args.beam_size_2)
            # print("Searching time:", time.time() - s2)

            # logger.info(f"MIPS searching: {time.time() - search_start}")
            D_ = D_.reshape(bsize, args.beam_size_1, args.beam_size_2)
            I_ = I_.reshape(bsize, args.beam_size_1, args.beam_size_2)

            # aggregate path scores
            path_scores = np.expand_dims(D, axis=2) + D_

            if args.hnsw:
                path_scores = - path_scores

            # path_scores = D_
            # eval
            for idx in range(bsize):
                search_scores = path_scores[idx]
                ranked_pairs = np.vstack(np.unravel_index(np.argsort(search_scores.ravel())[::-1], (args.beam_size_1, args.beam_size_2))).transpose()
                retrieved_titles = []
                hop1_titles = []
                paths, path_titles = [], []
                for _ in range(args.topk):
                    path_ids = ranked_pairs[_]
                    hop_1_id = I[idx, path_ids[0]]
                    hop_2_id = I_[idx, path_ids[0], path_ids[1]]
                    retrieved_titles.append(id2doc[str(hop_1_id)]["title"])
                    retrieved_titles.append(id2doc[str(hop_2_id)]["title"])

                    paths.append([str(hop_1_id), str(hop_2_id)])
                    path_titles.append([id2doc[str(hop_1_id)]["title"], id2doc[str(hop_2_id)]["title"]])
                    hop1_titles.append(id2doc[str(hop_1_id)]["title"])
                
                if args.only_eval_ans:
                    gold_answers = batch_ann[idx]["answer"]
                    concat_p = "yes no "
                    for p in paths:
                        concat_p += " ".join([id2doc[doc_id]["title"] + " " + id2doc[doc_id]["text"] for doc_id in p])
                    metrics.append({
                        "question": batch_ann[idx]["question"],
                        "ans_recall": int(para_has_answer(gold_answers, concat_p, simple_tokenizer)),
                        "type": batch_ann[idx].get("type", "single")
                    })
                    
                else:

                    sp = batch_ann[idx]["sp"]
                    assert len(set(sp)) == 2
                    type_ = batch_ann[idx]["type"]
                    question = batch_ann[idx]["question"]
                    p_recall, p_em = 0, 0
                    sp_covered = [sp_title in retrieved_titles for sp_title in sp]
                    if np.sum(sp_covered) > 0:
                        p_recall = 1
                    if np.sum(sp_covered) == len(sp_covered):
                        p_em = 1
                    path_covered = [int(set(p) == set(sp)) for p in path_titles]
                    recall_1 = 0
                    covered_1 = [sp_title in hop1_titles for sp_title in sp]
                    if np.sum(covered_1) > 0: recall_1 = 1
                    metrics.append({
                    "question": question,
                    "p_recall": p_recall,
                    "p_em": p_em,
                    "type": type_,
                    'recall_1': recall_1,
                    })


                    # gold_answers = batch_ann[idx]["answer"]
                    # sp_chain = [{"title":sp[0], "text": title2text[sp[0]]}, {"title":sp[1], "text": title2text[sp[1]]}]
                    # covered_k = {}
                    # for k in [1,5,10,20,50,100]:
                    #     covered_k[str(k)] = metrics[-1][f"path_covered_{k}"]

                    # saving when there's no annotations
                    if args.save_path != "":
                        candidaite_chains = []
                        for path in paths:
                            candidaite_chains.append([id2doc[path[0]], id2doc[path[1]]])
                        
                        retrieval_outputs.append({
                            "_id": batch_ann[idx]["_id"],
                            "question": batch_ann[idx]["question"],
                            "candidate_chains": candidaite_chains,
                            # "sp": sp_chain,
                            # "answer": gold_answers,
                            # "type": type_,
                            # "coverd_k": covered_k
                        })

    if args.save_path != "":
        with open(f"/private/home/xwhan/data/hotpot/{args.save_path}", "w") as out:
            for l in retrieval_outputs:
                out.write(json.dumps(l) + "\n")

    logger.info(f"Evaluating {len(metrics)} samples...")
    type2items = collections.defaultdict(list)
    for item in metrics:
        type2items[item["type"]].append(item)
    if args.only_eval_ans:
        logger.info(f'Ans Recall: {np.mean([m["ans_recall"] for m in metrics])}')
        for t in type2items.keys():
            logger.info(f"{t} Questions num: {len(type2items[t])}")
            logger.info(f'Ans Recall: {np.mean([m["ans_recall"] for m in type2items[t]])}')
    else:
        logger.info(f'Avg PR: {np.mean([m["p_recall"] for m in metrics])}')
        logger.info(f'Avg P-EM: {np.mean([m["p_em"] for m in metrics])}')
        logger.info(f'Avg 1-Recall: {np.mean([m["recall_1"] for m in metrics])}')
        logger.info(f'Path Recall: {np.mean([m["path_covered"] for m in metrics])}')
        for t in type2items.keys():
            logger.info(f"{t} Questions num: {len(type2items[t])}")
            logger.info(f'\tAvg PR: {np.mean([m["p_recall"] for m in type2items[t]])}')
            logger.info(f'\tAvg P-EM: {np.mean([m["p_em"] for m in type2items[t]])}')
            logger.info(f'Avg 1-Recall: {np.mean([m["recall_1"] for m in type2items[t]])}')
            logger.info(f'Path Recall: {np.mean([m["path_covered"] for m in type2items[t]])}')