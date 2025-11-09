import torch




def mask_from_lens(lens, max_len=None):
    """
    Create a boolean mask tensor from a tensor of lengths.
    Each position less than the length is True, otherwise False.
    """
    if not torch.is_tensor(lens):
        lens = torch.tensor(lens, dtype=torch.long)
    batch_size = lens.size(0)
    max_len = max_len or lens.max().item()
    ids = torch.arange(0, max_len, device=lens.device)
    mask = (ids.unsqueeze(0) < lens.unsqueeze(1))
    return mask


def maximum_path(value, mask):
    """Compute maximum path alignment."""
    device = value.device
    dtype = value.dtype

    value = value.transpose(0, 1).contiguous()
    mask = mask.transpose(0, 1).contiguous()

    t_t, t_s = value.size(0), value.size(1)
    direction = torch.zeros((t_t, t_s), dtype=torch.int64, device=device)
    score = torch.full((t_t, t_s), -1e9, dtype=dtype, device=device)

    score[0, 0] = value[0, 0]
    for t in range(1, t_t):
        score[t, 0] = score[t - 1, 0] + value[t, 0]
    for s in range(1, t_s):
        score[0, s] = score[0, s - 1] + value[0, s]

    for t in range(1, t_t):
        for s in range(1, t_s):
            left = score[t, s - 1]
            up = score[t - 1, s]
            if left > up:
                score[t, s] = left + value[t, s]
                direction[t, s] = 1
            else:
                score[t, s] = up + value[t, s]
                direction[t, s] = 2

    mask = mask.to(torch.bool)
    score = score * mask + (1 - mask) * -1e9
    return score.transpose(0, 1)
