var checkIfCanBeEncoded = (input, encoding) => {
    return !cptable.utils.encode(encoding, input).includes(0)
}