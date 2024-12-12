@bot.callback_query_handler(func=lambda call: call.data == 'INFO')
def info_menu(call):
    """
    Muestra información sobre el objeto perdido y permite cambiar su estado.
    """
    update_state(call.message.chat.id, 'INFO')
    
    # Aquí asumimos que el usuario tiene un objeto perdido asociado
    # En un caso real, deberías obtener el ID del objeto de alguna manera
    # Por simplicidad, vamos a asumir que el ID es 1
    object_id = 1
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM object_report WHERE rowid = ?", (object_id,))
        result = cursor.fetchone()
        connection.close()

        if result:
            # Interpretar el valor de 'found'
            status_message = "El objeto está en la caseta." if result[1] == 0 else "El objeto ha sido devuelto al dueño."

            image_url = result[2] if result[2] != 'null' else None

            message_text = f"Estado del objeto:\n" \
                           f"ID: {object_id}\n" \
                           f"Descripción: {result[4]}\n" \
                           f"Ubicación: {result[5]}\n" \
                           f"Fecha: {result[6]}\n" \
                           f"{status_message}"

            markup = types.InlineKeyboardMarkup()
            if result[1] == 0:  # Si el objeto está perdido, podemos cambiar su estado
                button = types.InlineKeyboardButton("Marcar como entregado", callback_data=f'CHANGE_STATUS_{object_id}')
                markup.add(button)

            if image_url and image_url != 'null':
                try:
                    bot.send_photo(call.message.chat.id, image_url, caption=message_text, reply_markup=markup)
                except Exception as e:
                    bot.send_message(call.message.chat.id, f"{message_text}\n\nImagen no disponible.", reply_markup=markup)
            else:
                bot.send_message(call.message.chat.id, f"{message_text}\n\nImagen no disponible.", reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, "No se encontró ningún objeto con ese ID.")
    
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Hubo un error al buscar el objeto. Error: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('CHANGE_STATUS_'))
def change_status(call):
    """
    Cambia el estado del objeto a entregado.
    """
    object_id = call.data.split('_')[-1]
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE object_report SET found = 1 WHERE rowid = ?", (object_id,))
        connection.commit()
        connection.close()
        
        bot.send_message(call.message.chat.id, f"El estado del objeto con ID {object_id} ha sido cambiado a entregado.")
    
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Hubo un error al cambiar el estado del objeto. Error: {e}")