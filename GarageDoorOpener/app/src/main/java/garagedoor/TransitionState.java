package garagedoor;

public enum TransitionState {
    ENTER(0),
    EXIT(1),
    DWELL(2),
    BUTTON(3);

    private final int value;

    TransitionState(int value) {
        this.value = value;
    }
    public int getValue() {
        return value;
    }
};
