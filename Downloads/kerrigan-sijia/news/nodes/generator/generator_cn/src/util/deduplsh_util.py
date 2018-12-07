import binascii
import random
import jieba


def write_lsh_redis(message, redis_cli, lsh_look_table, ts):
    article = Article(message)
    article.article_init(LSHEnvironment())
    lsh_keys = [LSHEnvironment.get_key(i, bind_signature)
                for i, bind_signature in enumerate(article.band_signatures)]
    with redis_cli.pipeline() as pipe:
        for lsh_key in lsh_keys:
            pipe.hset(lsh_look_table, lsh_key, message['account'])
            pipe.hset(lsh_look_table + '_ts', lsh_key, ts)
        pipe.execute()


class LSHEnvironment:
    def __init__(self):
        self.num_hash = 20
        self.band_num = 4
        self.row_num = 5
        self.default_section = 24 * 3600
        self.max_shingle_ID = 2 ** 32 - 1
        self.next_prime = 4294967311

        self.hash_function_list = HashFunction.get_hash_functions(
            num_hash=self.num_hash,
            max_shingle_ID=self.max_shingle_ID,
            next_prime=self.next_prime)
        self.band_hash_function = BandHashFunction(
            band_num=self.band_num,
            row_num=self.row_num,
            next_prime=self.next_prime)

    @staticmethod
    def get_key(band_index, band_signature):
        return '%s#%s' % (band_index, band_signature)


class HashFunction:
    @classmethod
    def get_hash_functions(cls, num_hash, max_shingle_ID, next_prime):
        return [cls(i, max_shingle_ID, next_prime) for i in range(num_hash)]

    def __init__(self, seed, max_shingle_ID, next_prime):
        self.max_shingle_ID = max_shingle_ID
        self.next_prime = next_prime
        self.seed = seed
        random.seed(self.seed)
        self.a = random.randint(0, max_shingle_ID)
        self.b = random.randint(0, max_shingle_ID)

    def init_hash(self):
        return self.next_prime + 1

    def hash(self, shingle_ID):
        return (self.a * shingle_ID + self.b) % self.next_prime


class BandHashFunction:
    def __init__(self, row_num, band_num, next_prime):
        self.row_num = row_num
        self.band_num = band_num
        self.next_prime = next_prime

    def get_band_hash(self, hash_signatures):
        band_hashes = []
        for band_index in range(self.band_num):
            band_hash = 0
            for row_index in range(self.row_num):
                for index in range(len(hash_signatures)):
                    band_hash = (band_hash + hash_signatures[self.row_num * band_index + row_index]) % self.next_prime
            band_hashes.append(band_hash)
        return band_hashes


class Article:
    @classmethod
    def get_article_instance(cls, account, content):
        message = {'account': account,
                   'content': [{'text': content}],
                   'title': ''}
        return cls(message)

    @staticmethod
    def compare_hash_signatrue(article1, article2):
        if len(article1.hash_signatures) != len(article2.hash_signatures):
            raise Exception
        else:
            num_hash = len(article1.hash_signatures)
            count = 0
            for i in range(num_hash):
                count += article1.hash_signatures[i] == article2.hash_signatures[i]
            return float(count) / num_hash

    def __init__(self, message):
        content = message['title'] + message['content']
        account = message['account']
        self.account = account
        self.content = content
        self.shingles = None
        self.hash_signatures = None
        self.band_signatures = None

    def article_init(self, lsh_environment):
        self._content_to_shingles()
        self._shingle_to_hash_signature(lsh_environment.hash_function_list)
        self._hash_signature_to_band_signature(lsh_environment.band_hash_function)
        return self

    def _content_to_shingles(self):
        # jieba will return unicode string
        cuted_words = [word.encode('utf-8') for word in list(jieba.cut(self.content))]
        shingle_in_content = set()
        for i in range(0, len(cuted_words) - 2):
            shingle = cuted_words[i] + ' ' + cuted_words[i + 1] + ' ' + cuted_words[i + 2]
            crc = binascii.crc32(shingle) & 0xffffffff
            shingle_in_content.add(crc)
        self.shingles = shingle_in_content

    def _shingle_to_hash_signature(self, hash_function_list):
        self.hash_signatures = []
        for i in range(0, len(hash_function_list)):
            this_func = hash_function_list[i]
            min_hash_code = this_func.init_hash()
            for shingle_ID in self.shingles:
                hash_code = this_func.hash(shingle_ID)
                if hash_code < min_hash_code:
                    min_hash_code = hash_code
            self.hash_signatures.append(min_hash_code)

    def _hash_signature_to_band_signature(self, band_hash_function):
        self.band_signatures = band_hash_function.get_band_hash(self.hash_signatures)

    def show_content(self):
        print str(self)
        print self.content

    def __str__(self):
        result = 'account: ' + self.account + '; hash_signature:' + str(self.hash_signatures)
        return result
