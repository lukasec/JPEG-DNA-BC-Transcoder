#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author : Romain Graux - modified by Luka Secilmis
"""

import requests
import numpy as np
from tqdm import tqdm
from time import sleep

import hydra
from omegaconf import OmegaConf, DictConfig

from functools import partial, lru_cache
from multiprocessing.pool import ThreadPool
from multiprocessing import cpu_count
import multiprocessing as mp

from typing import Union, Generator, Iterable, List, Tuple, Dict, Any

oligo_length = 200

class AttrDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __init__(self, data, *args, **kwargs):
        if kwargs.pop("_recursively", True):
            super().__init__(AttrDict._map(data), *args, **kwargs)
        else:
            super().__init__(data, *args, **kwargs)

    @classmethod
    def _map(cls, data: Any) -> Union[Dict, Any]:
        """Recursively convert all dicts to AttrDict"""
        if type(data) not in (dict, list, tuple):
            return data
        elif type(data) is list:
            return [cls._map(item) for item in data]
        elif type(data) is tuple:
            return tuple(cls._map(item) for item in data)
        return AttrDict(
            {key: cls._map(value) for key, value in data.items()}, _recursively=False
        )


class MESAResponse:
    def __init__(self, response):
        self._response = response
        self._status_code = response.status_code

    @property
    @lru_cache(maxsize=1)
    def _json(self) -> AttrDict:
        """Lazy load json"""
        return AttrDict(self._response.json())

    @property
    @lru_cache(maxsize=1)
    def sequence(self) -> str:
        keys = list(self._json.keys())
        assert len(keys) == 1, f"Expected 1 key, got {len(keys)} keys ({keys})"
        return keys[0]

    @property
    @lru_cache(maxsize=1)
    def modified_sequence(self) -> str:
        return self._json[self.sequence].res.modified_sequence

    def is_ok(self) -> bool:
        return self._status_code == 200

    def __repr__(self) -> str:
        return (
            f"<MESAResponse status_code={self._status_code} sequence={self.sequence}>"
        )

    def __str__(self) -> str:
        return repr(self)


class MESASimulator:
    def __init__(self, config: DictConfig):
        self.__config = config

    def set_config(self, key: str, value: Any):
        self.__config.__setattr__(key, value)

    @property
    def n_workers(self) -> int:
        nb = self.__config.connection.n_workers
        return cpu_count() if nb == "all" else int(nb)

    def _ensure_valid_sequences(self, sequences: Union[List, Tuple]):
        for sequence in sequences:
            assert set(sequence).issubset(
                set("ACGT")
            ), f'The sequence "{sequence}" is not valid since it is not containing only A, C, G or T'

    def _get_url(self, route: str) -> str:
        assert route.startswith("/"), "The route needs to start with /"
        return f'http{"s" if self.__config.connection.secure else ""}://{self.__config.connection.host}:{self.__config.connection.port}{route}'

    def get_config(self, key: str = None) -> Dict:
        conf = self.__config
        if key is not None:
            conf = self.__config.__getattr__(key)
        return OmegaConf.to_object(conf)

    def post(
        self, data: Union[dict, Iterable[dict]], route: str
    ) -> Union[requests.Response, List[requests.Response]]:
        global post_worker

        def post_worker(data: dict, url: str, config: Dict) -> requests.Response:
            json = config | data

            x = 0
            exit_ = 0
            while x == 0:
                try:
                    r = requests.post(url, json=json)
                    if(r.status_code == 200): 
                        x = 1
                    if r.status_code != 200:
                        x = 0 
                        print(f'Going to sleep - status: {r.status_code}')
                        sleep(20)
                        exit_ += 1
                        if exit_ == 10:
                            return None
                except: 
                    pass
            return r


        url = self._get_url(route)
        config = self.get_config("post")

        if type(data) is dict:
            return post_worker(data, url, config)

        with ThreadPool(self.n_workers) as p:
            f = partial(post_worker, url=url, config=config)
            responses = p.map(f, data)

        return responses

    def simulate(self, sequences: Union[str, List, Tuple]) -> MESAResponse:
        sequences = sequences if type(sequences) in (list, tuple, np.ndarray) else [sequences]
        #print(f"Simulating {sequences}")
        self._ensure_valid_sequences(sequences)
        data_sequences = [{"sequence": sequence} for sequence in sequences]
        responses = self.post(data_sequences, "/api/all")
        return (
            [MESAResponse(response) for response in responses]
            if len(sequences) > 1
            else MESAResponse(responses[0])
        )


@hydra.main(config_path="simulator", config_name="default.yaml")
def main(config: dict) -> None:
    global mesa, conf, result, dna_seq, dna_seq_split
    conf = config
    mesa = MESASimulator(config)

    with open("/input", "r") as fd:
        dna_seq = fd.read()

    # For the sequential simulation, sometimes it fails 
    # so we save our current simulated progress and then continue where we left off from (n)
    # Comment these 5 lines of code below if you are only starting the simulation. 
    # The program will quit when it has gone to sleep more than ten times. Next time you re-run it, uncomment the following lines
    #n = 0
    #with open("/output_already_started_writing_on_it", "r") as fd:
        #sim_sofar = fd.read()
        #n = len(sim_sofar)
    #dna_seq = dna_seq[n:]
    #################################################################################################
    
    
    dna_seq_split = [dna_seq[i:i+ oligo_length] for i in range(0, len(dna_seq), oligo_length)]
    
    print('Simulating ------------------------------------------------------------------')

    # Sequential Simulation
    result = []
    for i in range(len(dna_seq_split)):
        print(f'{(i)} / {len(dna_seq_split) - 1}')
        result = mesa.simulate(dna_seq_split[i]).modified_sequence
        if result is None: break
        with open("/output", "a") as fd:
            fd.write(result)
    
    # Multiprocessed Simulation
    # If able to use multiprocessing - modify n_workers to MESA_sim/connection/non_secure_local.yaml
    # Currently n_workers = 1
    # result = mesa.simulate(dna_seq_split)
    # result = [r.modified_sequence for r in result].join('')
    #with open("/output", "w") as fd:
            #fd.write(result)
    
    print('Done -------------------------------------------------------------------------')

if __name__ == "__main__":
    main()
