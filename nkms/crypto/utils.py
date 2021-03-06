import msgpack


class BytestringSplitter(object):
    def __init__(self, *message_types):
        """
        :param message_types:  A collection of types of messages to parse.
        """
        self.message_types = message_types

    def __call__(self, splittable, return_remainder=False, msgpack_remainder=False):
        if not any((return_remainder, msgpack_remainder)) and len(self) != len(splittable):
            raise ValueError(
                "Wrong number of bytes to constitute message types {} - need {}, got {} \n Did you mean to return the remainder?".format(
                    self.message_types, len(self), len(splittable)))
        if len(self) > len(splittable):
            raise ValueError(
                "Not enough bytes to constitute message types {} - need {}, got {}".format(self.message_types,
                                                                                           len(self),
                                                                                           len(splittable)))
        cursor = 0
        message_objects = []

        for message_type in self.message_types:
            message_class, message_length = self.get_message_meta(message_type)
            expected_end_of_object_bytes = cursor + message_length
            bytes_for_this_object = splittable[cursor:expected_end_of_object_bytes]
            message = message_class(bytes_for_this_object)

            message_objects.append(message)
            cursor = expected_end_of_object_bytes

        remainder = splittable[cursor:]

        if msgpack_remainder:
            message_objects.append(msgpack.loads(remainder))
        elif return_remainder:
            message_objects.append(remainder)

        return message_objects

    def __len__(self):
        return sum(self.get_message_meta(m)[1] for m in self.message_types)

    @staticmethod
    def get_message_meta(message_type):
        return message_type if isinstance(message_type, tuple) else (message_type, message_type._EXPECTED_LENGTH)
