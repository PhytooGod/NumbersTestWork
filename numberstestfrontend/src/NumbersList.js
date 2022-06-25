import React, {useState, useEffect} from 'react'
import { Table } from 'reactstrap';

const NumbersList = () => {

	let [numbers, setNumbers] = useState([])

	useEffect(() => {
		getNumbers();

        const interval = setInterval(() => {
            getNumbers();
        }, 1000 * 10)

        return () => {
            clearInterval(interval);
        }
	}, [])

	let getNumbers = async () => {
		let response = await fetch('http://localhost:80/numberstest/numbers/')
		let data = await response.json()
        console.log(data)
		setNumbers(data)
	}

    document.body.style = 'background:#212529;';

	return (
		<div>
			<Table dark>
				<thead>
					<tr>
						<td> № </td>
						<td> Номер заказа </td>
						<td> Стоимость в долларах </td>
						<td> срок поставки </td>
						<td> Стоимость в рублях </td>
					</tr>
				</thead>
				<tbody>
				{numbers.map((number, index) => (
					<tr key={index}>
						<td> {number.num} </td>
						<td> {number.order_number} </td>
						<td> {number.price_dollar} </td>
						<td> {number.supply_date} </td>
						<td> {number.price_ruble} </td>
					</tr>
				))}
				</tbody>
			</Table>
		</div>
	)
}

export default NumbersList