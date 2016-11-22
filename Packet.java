public class Packet {

    int seqNum;
    boolean isAcked;
    byte[] data;
    int resentCounter;


    public Packet(seqNum, isAcked, data, resentCounter) {
        this.seqNum = seqNum;
        this.isAcked = isAcked;
        this.data = data;
        this.resentCounter = resentcounter;
    }

    public void setSeqNum(int seqNum) {
        this.seqNum = seqNum;
    }

    public void setAck(boolean isAcked) {
        this.isAcked = isAcked;
    }
}
