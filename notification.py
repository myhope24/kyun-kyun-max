import requests
import re

class Notification:
    def send_lotto_buying_message(self, body: dict, token: str, channel: str) -> None:
        assert type(token) == str
        assert type(channel) == str

        result = body.get("result", {})
        if result.get("resultMsg", "FAILURE").upper() != "SUCCESS":  
            return

        lotto_number_str = self.make_lotto_number_message(result["arrGameChoiceNum"])
        message = f"{result['buyRound']}회 로또 구매 완료 :moneybag: 남은잔액 : {body['balance']}\n```{lotto_number_str}```"
        self._send_slack_webhook(token, channel, message)

    def make_lotto_number_message(self, lotto_number: list) -> str:
        assert type(lotto_number) == list

        # parse list without last number 3
        lotto_number = [x[:-1] for x in lotto_number]
        
        # remove alphabet and | replace white space  from lotto_number
        lotto_number = [x.replace("|", " ") for x in lotto_number]
        
        # lotto_number to string 
        lotto_number = '\n'.join(x for x in lotto_number)
        
        return lotto_number

    def send_win720_buying_message(self, body: dict, token: str, channel: str) -> None:
        assert type(token) == str
        assert type(channel) == str
        
        if body.get("resultCode") != '100':  
            return       

        win720_round = body.get("resultMsg").split("|")[3]

        win720_number_str = self.make_win720_number_message(body.get("saleTicket"))
        message = f"{win720_round}회 연금복권 구매 완료 :moneybag: 남은잔액 : {body['balance']}\n```\n{win720_number_str}```"
        self._send_slack_webhook(token, channel, message)

    def make_win720_number_message(self, win720_number: str) -> str:
        formatted_numbers = []
        for number in win720_number.split(","):
            formatted_number = f"{number[0]}조 " + " ".join(number[1:])
            formatted_numbers.append(formatted_number)
        return "\n".join(formatted_numbers)

    def send_lotto_winning_message(self, winning: dict, token: str, channel: str) -> None: 
        assert type(winning) == dict
        assert type(token) == str
        assert type(channel) == str

        try: 
            round = winning["round"]
            money = winning["money"]

            max_label_status_length = max(len(f"{line['label']} {line['status']}") for line in winning["lotto_details"])

            formatted_lines = []
            for line in winning["lotto_details"]:
                line_label_status = f"{line['label']} {line['status']}".ljust(max_label_status_length)
                line_result = line["result"]

                formatted_nums = []
                for num in line_result:
                    raw_num = re.search(r'\d+', num).group()
                    formatted_num = f"{int(raw_num):02d}"
                    if '✨' in num:
                        formatted_nums.append(f"[{formatted_num}]")
                    else:
                        formatted_nums.append(f" {formatted_num} ")

                formatted_nums = [f"{num:>6}" for num in formatted_nums]

                formatted_line = f"{line_label_status} " + " ".join(formatted_nums)
                formatted_lines.append(formatted_line)

            formatted_results = "\n".join(formatted_lines)

            if winning['money'] != "-":
                winning_message = f"로또 *{winning['round']}회* - *{winning['money']}* 당첨 되었습니다 🎉"
                self._send_slack_webhook(token, channel, winning_message)
            else:
                winning_message = f"로또 *{winning['round']}회* - 다음 기회에... 🫠"

        except KeyError:
            return

    def send_win720_winning_message(self, winning: dict, token: str, channel: str) -> None: 
        assert type(winning) == dict
        assert type(token) == str
        assert type(channel) == str

        try: 
            round = winning["round"]
            money = winning["money"]

            if winning['money'] != "-":
                message = f"연금복권 *{winning['round']}회* - *{winning['money']}* 당첨 되었습니다 🎉"

            self._send_slack_webhook(token, channel, message)                                                                       
        except KeyError:
            message = f"연금복권 - 다음 기회에... 🫠"
            #self._send_slack_webhook(token, channel, message)
            return

    def _send_slack_webhook(self, token: str, channel: str, message: str) -> None:        
        payload = { "text": message, "channel": channel }
        headers = { "Content-Type": "application/json", "Authorization": f"Bearer {token}" }
        requests.post("https://slack.com/api/chat.postMessage", json=payload, headers=headers)
