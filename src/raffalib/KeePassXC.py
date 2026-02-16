# raffalib-python Miscellaneous functions
# Copyright (C) 2026 Raffaele Mancuso
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import base64
import json
import logging
# WARNING: This is python-gnupg (https://pypi.org/project/python-gnupg/)
#          NOT gnupg (https://pypi.org/project/gnupg/)
import gnupg as python_gnupg
import keepassxc_proxy_client
import keepassxc_proxy_client.protocol
from keepassxc_proxy_client.protocol import ResponseUnsuccesfulException

class KeePassXC:
    """
    This class creates a KeePassXC association and store it in an encrypted file

    The encrypted file is written in the following format:
    * A JSON object with two fields is created
    * The first field is the name of the association (the string
      "raffaele.mancuso4@unibo.it")
    * The second field is the public key of the association, encoded in
      base64 ASCII
    * The JSON object is then encrypted with GPG using the public key of
      the email address specified in the first field
    * The encrypted message is then written to the file

    The constructor takes the following parameters:
    * kpxcencfp: the path to the file that will contain the encrypted
      association
    * gpg_passphrase: the GPG passphrase to use for encryption
    * newgpg: an existing gnupg.GPG object to use. If None, a new one is
      created
    """

    def __init__(
        self, kpxcencfp, gpg_passphrase=None, newgpg=None
    ):
        """
        Initializes a KeePassXC association, either by creating a new one
        or loading an existing one from an encrypted file.

        Args:
            kpxcencfp: Path to the file for storing the encrypted association.
            gpg_passphrase: The GPG passphrase used for decryption.
            newgpg: An optional existing gnupg.GPG object to use.
        """
        # Initialize GPG object
        self.gpg = newgpg if newgpg else python_gnupg.GPG()

        # Establish a connection to KeePassXC
        self.keepassxc = keepassxc_proxy_client.protocol.Connection()

        # Attempt to connect to KeePassXC
        try:
            self.keepassxc.connect()
        except FileNotFoundError:
            raise Exception("KeePassXC is either not open or is open but browser integration is not enabled")

        # Retrieve database hash to ensure the database is opened
        try:
            dbhash = self.keepassxc.get_databasehash()
            logging.debug("Database hash: " + dbhash)
        except ResponseUnsuccesfulException:
            raise Exception("Database not opened")

        # If the file for storing the association does not exist, create a new association
        if not kpxcencfp.is_file():
            logging.debug("Creating new KeePassXC association")
            self.keepassxc.associate()
            logging.debug("Test associate: " + str(self.keepassxc.test_associate()))
            assert self.keepassxc.test_associate()

            # Dump the association details
            name, public_key = self.keepassxc.dump_associate()

            # Encode the public key in base64
            public_key_str = base64.b64encode(public_key).decode("ascii")
            outd = {"name": name, "pk": public_key_str}
            outdd = json.dumps(outd, ensure_ascii=False, indent=4, sort_keys=True)

            # Encrypt the JSON object
            outenc = self.gpg.encrypt(outdd, "raffaele.mancuso4@unibo.it")
            if not outenc.ok:
                raise Exception("GPG returned an error. Is the private key enrolled within GPG?")

            # Write the encrypted message to the file
            message = outenc.data.decode("utf8")
            with open(kpxcencfp, "w") as fh:
                fh.write(message)
        else:
            # Load an existing association from the encrypted file
            logging.debug("Reading existing KeePassXC association from file")
            with open(kpxcencfp, "r") as fh:
                data = fh.read()

            # Decrypt the message
            outdd = self.gpg.decrypt(data, passphrase=gpg_passphrase)
            if not outdd.ok:
                msg = f"Failed to decrypt file '{kpxcencfp}'\n"
                msg += f"outdd.ok='{outdd.ok}'\n"
                msg += f"outdd.status='{outdd.status}'\n"
                raise Exception(msg)

            # Decode the message and load the association
            message = outdd.data.decode("utf8")
            outd = json.loads(message)
            self.keepassxc.load_associate(
                name=outd["name"],
                public_key=base64.b64decode(outd["pk"])
            )

            # Test the loaded association
            if not self.keepassxc.test_associate():
                msg = f"Failed to associate key read from file '{kpxcencfp}'\n"
                raise Exception(msg)
