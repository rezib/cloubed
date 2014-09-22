from xml.dom.minidom import Document, parseString
from libvirt import libvirtError

class MockConfigurationLoader:

    def __init__(self, content):

        self.content = content

    def get_content(self):

        return self.content

    def remove(self, key):

        self.content.pop(key, None)

class MockLibvirt():

    """Class with static methods to mock all used functions in libvirt module"""

    version = 8006

    def __init__(self):
        pass

    @staticmethod
    def open(hyp):
        """Mock of libvirt.open(name)"""
        return MockLibvirtConnect(hyp)
        #pass

    @staticmethod
    def openReadOnly(hyp):
        """Mock of libvirt.openReadOnly(name)"""
        return MockLibvirtConnect(hyp, read_only=True)
        #pass

    @staticmethod
    def virEventRegisterDefaultImpl():
        """Mock of libvirt.virEventRegisterDefaultImpl()"""
        pass

    @staticmethod
    def virEventRunDefaultImpl():
        """Mock of libvirt.virEventRunDefaultImpl()"""
        pass

    @staticmethod
    def getVersion():
        """Mock of libvirt.getVersion()"""
        return MockLibvirt.version

class MockLibvirtConnect():

    """Class to mock libvirt.virConnect class and its methods used in Cloubed"""

    def __init__(self, hyp, read_only=False):

        self.hyp = hyp
        self.ro = read_only

        self.pools = []
        self.defined_pools = []

        self.networks = []
        self.defined_networks = []

        self.domains = []
        self.defined_domains = []

    def listStoragePools(self):
        """Mock of libvirt.virConnect.listStoragePools()"""

        return [ pool._name for pool in self.pools ]

    def listDefinedStoragePools(self):
        """Mock of libvirt.virConnect.listDefinedStoragePools()"""

        return [ pool._name for pool in self.defined_pools ]

    def storagePoolLookupByName(self, path):
        """Mock of libvirt.virConnect.storagePoolLookupByName()"""
        try:
            return next((pool for pool in self.pools + self.defined_pools \
                              if pool.path == path))
        except StopIteration:
            raise libvirtError("Storage pool not found: no pool with matching" \
                               "name '{path}'".format(path=path))

    def storagePoolCreateXML(self, xml, flag):
        """Mock of libvirt.virConnect.storagePoolCreateXML()"""

        dom = parseString(xml)
        path = dom.getElementsByTagName(u'path')[0].firstChild.data
        pool = MockLibvirtStoragePool(path)
        self.pools.append(pool)

    def listNetworks(self):
        """Mock of libvirt.virConnect.listNetworks()"""

        return [ network.name for network in self.networks ]

    def listDefinedNetworks(self):
        """Mock of libvirt.virConnect.listDefinedNetworks()"""

        return [ network.name for network in self.defined_networks ]

    def networkLookupByName(self, name):
        """Mock of libvirt.virConnect.networkLookupByName()"""

        try:
            return next((net for net in self.networks + self.defined_networks \
                             if net.name == name))
        except StopIteration:
            raise libvirtError("Network not found: no network with matching" \
                               "name '{name}'".format(name=name))

    def networkCreateXML(self, xml):
        """Mock of libvirt.virConnect.networkCreateXML()"""

        dom = parseString(xml)
        name = dom.getElementsByTagName(u'name')[0].firstChild.data
        net = MockLibvirtNetwork(name)
        self.networks.append(net)

    def listDomainsID(self):
        """Mock of libvirt.virConnect.listDomainsID()"""

        return [ domain.id for domain in self.domains ]

    def listDefinedDomains(self):
        """Mock of libvirt.virConnect.listDefinedDomains()"""

        return [ domain._name for domain in self.defined_domains ]

    def lookupByID(self, id):
        """Mock of libvirt.virConnect.lookupByID()"""

        try:
            return next((domain for domain \
                                in self.domains + self.defined_domains \
                                if domain.id == id))
        except StopIteration:
            raise libvirtError("Domain not found: no domain with matching" \
                               "id {id}".format(id=id))

    def lookupByName(self, name):
        """Mock of libvirt.virConnect.lookupByName()"""

        try:
            return next((domain for domain \
                                in self.domains + self.defined_domains \
                                if domain._name == name))
        except StopIteration:
            raise libvirtError("Domain not found: no domain with matching" \
                               "name '{name}'".format(name=name))

    def createXML(self, xml, flags):
        """Mock of libvirt.virConnect.createXML()"""

        dom = parseString(xml)
        name = dom.getElementsByTagName(u'name')[0].firstChild.data
        domain = MockLibvirtDomain(len(self.domains), name)
        self.domains.append(domain)

    def setKeepAlive(self, major, minor):
        """Mock of libvirt.virConnect.setKeepAlive()"""

        pass

    def domainEventRegisterAny(self, dom, eventID, cb, opaque):
        """Mock of libvirt.virConnect.domainEventRegisterAny()"""

        pass

class MockLibvirtStoragePool():

    """Class to mock libvirt.virStoragePool class and its methods used in
       Cloubed
    """

    def __init__(self, name):

        self._name = name
        self.path = name
        self.volumes = []
        self.active = True

    def name(self):
        """Mock of libvirt.virStoragePool.name()"""

        return self._name

    def XMLDesc(self, flag):
        """Mock of libvirt.virStoragePool.XMLDesc()"""

        doc = Document()
        elt = doc.createElement("path")
        txt = doc.createTextNode(self.path)
        elt.appendChild(txt)
        doc.appendChild(elt)
        return doc.toxml()

    def listVolumes(self):
        """Mock of libvirt.virStoragePool.listVolumes()"""

        return self.volumes

    def storageVolLookupByName(self, name):
        """Mock of libvirt.virStoragePool.storageVolLookupByName()"""

        try:
            return next((vol for vol in self.volumes \
                             if vol == name))
        except StopIteration:
            raise libvirtError("Storage volume not found: no storage vol " \
                               "with matching name '{name}'".format(name=name))

    def createXML(self, xml, flag):
        """Mock of libvirt.virStoragePool.createXML()"""

        pass

    def isActive(self):
        """Mock of libvirt.virStoragePool.isActive()

           This method is used in StoragePool.destroy() and StoragePool.create()
        """

        return self.active

    def numOfVolumes(self):
        """Mock of libvirt.virStoragePool.numOfVolumes()

           This method is used in StoragePool.destroy()
        """

        return len(self.volumes)

    def info(self):
        """Mock of libvirt.virStoragePool.info()

           This method is used in VirtController.__info_storage_pool()
        """

        return [0,]

    def destroy(self):
        """Mock of libvirt.virStoragePool.destroy()

           This method is used in StoragePool.destroy()
        """

        pass

class MockLibvirtNetwork():

    """Class to mock libvirt.virNetwork class and its methods used in
       Cloubed
    """

    def __init__(self, name):

        self.name = name
        self.active = True

    def isActive(self):
        """Mock of libvirt.virNetwork.isActive()

           This method is used in VirtController.__info_network(),
           Network.destroy() and Network.create()
        """

        return self.active

    def destroy(self):
        """Mock of libvirt.virNetwork.destroy()

           This method is used in Network.destroy() and Network.create()
        """

        pass

    def XMLDesc(self, flag):
        """Mock of libvirt.virNetwork.XMLDesc()

           This method is used in VirtController.__info_network()
        """
        doc = Document()
        elt = doc.createElement("name")
        txt = doc.createTextNode(self.name)
        elt.appendChild(txt)
        doc.appendChild(elt)
        return doc.toxml()

class MockLibvirtDomain():

    """Class to mock libvirt.virDomain class and its methods used in
       Cloubed
    """

    def __init__(self, id, name):

        self.id = id
        self._name = name
        self.active = True

    def name(self):
        """Mock of libvirt.virDomain.name()"""

        return self._name

    def isActive(self):
        """Mock of libvirt.virDomain.isActive()

           This method is used in Domain.destroy() and Domain.create()
        """

        return self.active

    def destroy(self):
        """Mock of libvirt.virDomain.destroy()

           This method is used in Domain.destroy()
        """

        pass

    def info(self):
        """Mock of libvirt.virDomain.info()

           This method is used in VirtController.__info_domain()
        """

        return [0,]

    def XMLDesc(self, flag):
        """Mock of libvirt.virDomain.XMLDesc()

           This method is used in VirtController.__info_domain()
        """
        doc = Document()
        dom = doc.createElement("domain")
        doc.appendChild(dom)
        elt = doc.createElement("name")
        txt = doc.createTextNode(self._name)
        elt.appendChild(txt)
        dom.appendChild(elt)
        elt = doc.createElement("graphics")
        elt.setAttribute("type", "spice")
        elt.setAttribute("port", "5900")
        dom.appendChild(elt)
        return doc.toxml()
