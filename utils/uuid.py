from itertools import permutations, islice
from random import choice, shuffle
from string import ascii_uppercase, digits
from typing import Set, Dict, List
from math import factorial

from utils.singleton import Singleton

UUID_CHARSET = ascii_uppercase + digits
SAMPLE_SIZE = 1000


class UUIDGenerator(metaclass=Singleton):

    def __init__(self):
        self._generated_uuids: Dict[int, Set[str]] = {}

    def free_uuid(self, uuid: str):
        uuid_set: Set[str] = self._generated_uuids.get(len(uuid))
        if uuid_set:
            uuid_set.discard(uuid)
            if len(uuid_set) == 0:
                self._generated_uuids.pop(len(uuid), None)

    def get_uuid(self):
        current_size: int = 1
        while self._generated_uuids_is_full_for(current_size):
            current_size += 1

        # Try first with a random uuid to avoid generating permutations (which is costly)
        uuid: str = get_random_string(UUID_CHARSET, current_size)
        uuid_size_set: Set[str] = self._generated_uuids.get(current_size)
        if not uuid_size_set:
            self._generated_uuids[current_size] = set()
            self._generated_uuids[current_size].add(uuid)
            return uuid
        if uuid not in uuid_size_set:
            self._generated_uuids[current_size].add(uuid)
            return uuid

        # Permutations returns a generator
        # We get a sample of all possible permutations to avoid consuming the generator for big sizes
        all_possible_uuids = permutations(UUID_CHARSET, current_size)
        sample_possible_uuids: Set[str] = set(''.join(i) for i in islice(all_possible_uuids, SAMPLE_SIZE))

        candidate_uuids: Set[str] = sample_possible_uuids.difference(self._generated_uuids[current_size])
        while not candidate_uuids:
            sample_possible_uuids = set(''.join(i) for i in islice(all_possible_uuids, SAMPLE_SIZE))
            candidate_uuids = sample_possible_uuids.difference(self._generated_uuids[current_size])
        candidate_uuids_list: List[str] = list(candidate_uuids)
        shuffle(candidate_uuids_list)
        uuid = candidate_uuids_list.pop()
        uuid_size_set.add(uuid)
        return uuid

    def _generated_uuids_is_full_for(self, size: int) -> bool:
        if size not in self._generated_uuids.keys():
            return False

        # Check greater or equal just in case we add an extra key? Should not be possible but better safe than sorry
        return len(self._generated_uuids[size]) >= _get_permutations_number_for(UUID_CHARSET, size)


def _get_permutations_number_for(charset: str, size: int):
    return factorial(len(charset)) // factorial(len(charset) - size)


def get_random_string(charset: str, length: int) -> str:
    return ''.join(choice(charset) for _ in range(length))
