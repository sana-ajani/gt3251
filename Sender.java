import java.util.Collections;


public class Sender {

    private int windowSize;
    private int seqNum;
    private ArrayList packetQueue = new ArrayList();

    public void addToQueue() {
        Packet p = new Packet(seqNum++);
        packetQueue.put(p);
    }

    public void send() {

        while (windowSize = )
    }


}
