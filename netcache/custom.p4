/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header custom_t {
    bit<32>   ID;
    bit<32>   key;
    bit<32>   val;
    bit<32>   hit;
    bit<32>   responder_ID;
}

struct metadata {
    /* empty */
    bit<32> idx;
    bit<1> cacheHit;
    bit<32> hotKey;
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    custom_t custom;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition parse_custom;
    }

    state parse_custom {
	packet.extract(hdr.custom);
	transition accept;
    }

}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    bit<16> temp;
    bit<64> packet_count;
    register<bit<64>>(1) packet_counter;

    action key_match(bit<32> index) {
	meta.idx = index;
	hdr.custom.hit = 1;
	meta.cacheHit = 1;
	
	# Route Query back to the source
	hdr.ipv4.dstAddr = hdr.ipv4.srcAddr;
    }

    table key_lookup {
	key = {
	    hdr.custom.key: exact;
	}

	actions = {
	    key_match;
	    NoAction;
	}

	default_action = NoAction();
    }
    
    action drop() {
        mark_to_drop(standard_metadata);
    }

    action ipv4_forward(egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    table ipv4_exact {
	key = {
	    hdr.ipv4.dstAddr: exact;
	}	
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
    }

    apply {
	packet_counter.read(packet_count, 0);
	packet_counter.write(0, packet_count+1);
	
	if(hdr.custom.hit == 0) {
	    key_lookup.apply();
	}
	
	# Routing
        if(ipv4_exact.apply().miss) {
	    ipv4_lpm.apply();
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

#define COUNT_MIN_SIZE 1024

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    register<bit<32>>(32) cache;
    register<bit<32>>(32) keyCounter;
    register<bit<16>>(1) threshold_reg;
    bit<16> threshold;
    
    register<bit<16>>(1024) countMinArr1;
    register<bit<16>>(1024) countMinArr2;
    register<bit<16>>(1024) countMinArr3;
    register<bit<16>>(1024) countMinArr4;
    
    // register<bit<16>>(1024) bloomFilterArr;
    
    register<bit<32>>(1) hot_key;
    
    register<bit<32>>(1) switch_ID;
    
    bit<16> minVal;
    
    bit<32> keyIndex;
    
    bit<32> countMinIndex;
    
    action reportHotKey() {
    	#meta.hotKey = hdr.custom.key;
    	#digest(1, meta.hotKey);
    	bit<32> hot_key_val;
    	hot_key_val = (bit<32>)hdr.custom.val*65536 + (bit<32>)hdr.custom.key;
    	hot_key.write(0, hot_key_val);
    }
    
    action computeHash(HashAlgorithm algo) {
	hash(
	    countMinIndex,
	    algo,
	    (bit<1>) 0,
	    {
		hdr.custom.key	
	    },
	    (bit<16>) 65335
	);
    }

    action countMin() {
    	bit<16> countMinVal;
    	bit<16> val1;
    	bit<16> val2;
    	bit<16> val3;
    	bit<16> val4;
    	computeHash(HashAlgorithm.crc16);
    	countMinArr1.read(countMinVal, countMinIndex % COUNT_MIN_SIZE);
    	countMinArr1.write(countMinIndex % COUNT_MIN_SIZE, countMinVal+1);
        val1 = countMinVal + 1;
    	
    	computeHash(HashAlgorithm.crc32);
    	countMinArr2.read(countMinVal, countMinIndex % COUNT_MIN_SIZE);
    	countMinArr2.write(countMinIndex % COUNT_MIN_SIZE, countMinVal+1);
    	val2 = countMinVal + 1;
    	
    	computeHash(HashAlgorithm.xor16);
    	countMinArr3.read(countMinVal, countMinIndex % COUNT_MIN_SIZE);
    	countMinArr3.write(countMinIndex % COUNT_MIN_SIZE, countMinVal+1);
    	val3 = countMinVal + 1;
    	
    	computeHash(HashAlgorithm.csum16);
    	countMinArr4.read(countMinVal, countMinIndex % COUNT_MIN_SIZE);
    	countMinArr4.write(countMinIndex % COUNT_MIN_SIZE, countMinVal+1);
    	val4 = countMinVal + 1;
    	
    	minVal = val1;
    	if(val2 < minVal) {
	    minVal = val2;
	}
	if(val3 < minVal) {
	    minVal = val3;
	}
	if(val4 < minVal) {
	    minVal = val4;
	}
    }
    
    apply {
        # Cache Hit
    	if(meta.cacheHit == 1) {
	    keyIndex = meta.idx;
	    bit<32> val;
	    cache.read(val, keyIndex);
	    hdr.custom.hit = 1;
	    hdr.custom.val = val;
	    
	    bit<32> switch_ID_val;
	    switch_ID.read(switch_ID_val, 0);
	    hdr.custom.responder_ID = switch_ID_val;
	    
	    bit<32> prevCount;
	    keyCounter.read(prevCount, keyIndex);
	    keyCounter.write(keyIndex, prevCount+1);
	}
	
	if(meta.cacheHit == 0 && hdr.custom.hit == 1) {
	    countMin();
	    #cache.write(hdr.custom.key, (bit<32>)minVal);
	    threshold_reg.read(threshold, 0);
	    if(threshold < 3) {
	    	threshold = 3;
	    }
	    if(minVal > threshold) {
	    	reportHotKey();
	    }
	}
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
        update_checksum(
        hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
	packet.emit(hdr.custom);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
